<?php
/**
 * Webmention and Pingback collector endpoint.
 *
 * - Webmention: POST with form encoded 'source' and 'target' fields
 *   (https://www.w3.org/TR/webmention/)
 * - Pingback:   POST with an XML-RPC 'pingback.ping' body
 *               (https://www.hixie.ch/specs/pingback/pingback)
 *
 * Both are verified the same way (the source must be reachable and
 * link to the target) and stored in the same flat file store. The
 * source must answer with HTTP 200 after redirects, otherwise the
 * mention is not added. Optionally the source is then pushed to the
 * Internet Archive (best-effort, see config.php). There is
 * deliberately no read API - the collected data is harvested over the
 * deployment connection and merged by '#scripts/webmention/lint.py'.
 *
 * Responses: 202 accepted, 400 bad request, 422 verification failed
 * (source doesn't link back), 429 rate limited. Pingback requests are
 * answered with XML-RPC fault messages.
 */

declare(strict_types=1);

require __DIR__ . '/lib/store.php';
require __DIR__ . '/lib/verify.php';
require __DIR__ . '/lib/archive.php';

/** Verification failures carry a message and (pingback) fault code. */
final class wmVerificationException extends RuntimeException
{
    public function __construct(
        public readonly int $faultCode,
        string $message
    ) {
        parent::__construct($message);
    }
}

$config = require __DIR__ . '/config.php';

/** Sends a response body and status, then stops. */
function wmRespond(int $status, string $body, string $contentType = 'text/plain; charset=utf-8'): never
{
    http_response_code($status);
    header('Content-Type: ' . $contentType);
    echo $body;
    exit;
}

/** Sends an XML-RPC fault (used for pingback requests). */
function wmXmlRpcFault(int $code, string $message): never
{
    $message = htmlspecialchars($message, ENT_XML1);
    wmRespond(200, <<<XML
    <?xml version="1.0" encoding="utf-8"?>
    <methodResponse><fault><value><struct>
      <member><name>faultCode</name><value><int>$code</int></value></member>
      <member><name>faultString</name><value><string>$message</string></value></member>
    </struct></value></fault></methodResponse>
    XML, 'text/xml; charset=utf-8');
}

/** Builds a successful XML-RPC response body (used for pingback requests). */
function wmXmlRpcSuccessBody(string $message): string
{
    return <<<XML
    <?xml version="1.0" encoding="utf-8"?>
    <methodResponse><params><param><value>
      <string>$message</string>
    </value></param></params></methodResponse>
    XML;
}

/**
 * Releases the response the client already received (when running
 * under FPM) and runs the optional, best-effort Internet Archive save
 * of the mentioned source. A failing save must never affect what the
 * client saw - it only logs.
 */
function wmArchiveFinish(array $config, string $source): never
{
    if (function_exists('fastcgi_finish_request')) {
        fastcgi_finish_request();
    }
    wmArchiveSave($config, $source);
    exit;
}

/**
 * Full verification pipeline shared by both protocols. Throws a
 * wmVerificationException on any failure, returns the stored entry.
 */
function wmHandleMention(array $config, string $source, string $target, string $type): array
{
    if (!wmUrlValid($source) || !wmUrlValid($target)) {
        throw new wmVerificationException(16, 'Invalid source or target URL');
    }
    if (!wmUrlIsPublic($source, $config)) {
        throw new wmVerificationException(16, 'Invalid source URL');
    }
    $host = strtolower((string) parse_url($target, PHP_URL_HOST));
    if (!in_array($host, array_map('strtolower', $config['allowedDomains']), true)) {
        throw new wmVerificationException(32, 'Target not allowed');
    }
    $sourceDocument = wmFetchUrl($source, $config);
    if ($sourceDocument === null) {
        throw new wmVerificationException(16, 'Could not fetch source URL');
    }
    // Reachability gate: only pages that answer with HTTP 200 (after
    // redirects) can add mentions - dead or erroring sources are not
    // worth collecting.
    if ($sourceDocument['status'] !== 200) {
        throw new wmVerificationException(
            16,
            "Source URL is not reachable (HTTP $sourceDocument[status])"
        );
    }
    $html = $sourceDocument['body'];
    if (!wmFindBacklink($html, $source, $target)) {
        throw new wmVerificationException(17, 'Source does not link to target');
    }
    $mention = wmExtractEntry($html, $source, $type, $config);
    if (!wmStoreAdd($config, $target, $mention)) {
        throw new wmVerificationException(0, 'Storage failure');
    }
    return $mention;
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    header('Allow: POST');
    wmRespond(405, 'Method Not Allowed');
}

// Rate limit before anything else.
if (!wmRateLimitCheck($config, $_SERVER['REMOTE_ADDR'] ?? 'unknown')) {
    wmRespond(429, 'Too Many Requests');
}

$rawBody = (string) file_get_contents('php://input');
$contentType = strtolower($_SERVER['CONTENT_TYPE'] ?? '');

// Pingback (XML-RPC): params are (sourceURI, targetURI).
if (str_contains($contentType, 'xml') || str_contains($rawBody, 'pingback.ping')) {
    $xml = @simplexml_load_string($rawBody);
    if ($xml === false || (string) $xml->methodName !== 'pingback.ping') {
        wmXmlRpcFault(0, 'Unsupported XML-RPC method');
    }
    $params = $xml->xpath('//params/param/value/string');
    if ($params === false || count($params) < 2) {
        wmXmlRpcFault(0, 'Missing pingback parameters');
    }
    try {
        $mention = wmHandleMention($config, trim((string) $params[0]), trim((string) $params[1]), 'mention');
    } catch (wmVerificationException $exception) {
        wmXmlRpcFault($exception->faultCode, $exception->getMessage());
    }
    http_response_code(200);
    header('Content-Type: text/xml; charset=utf-8');
    echo wmXmlRpcSuccessBody('Pingback registered');
    wmArchiveFinish($config, $mention['source'] ?? '');
}

// Webmention: form encoded source/target.
$source = trim((string) ($_POST['source'] ?? ''));
$target = trim((string) ($_POST['target'] ?? ''));

if ($source === '' || $target === '') {
    wmRespond(400, 'Missing source or target');
}

// Honeypot: spam bots fill hidden fields - pretend success, drop silently.
$honeypot = $config['honeypotField'];
if ($honeypot !== '' && trim((string) ($_POST[$honeypot] ?? '')) !== '') {
    wmRespond(202, 'Accepted');
}

try {
    $mention = wmHandleMention($config, $source, $target, 'mention');
} catch (wmVerificationException $exception) {
    if ($exception->faultCode === 17) {
        wmRespond(422, $exception->getMessage());
    }
    wmRespond(400, $exception->getMessage());
}

// The client gets its 202 right away; the optional, best-effort
// Internet Archive save of the source follows and may fail freely.
http_response_code(202);
header('Content-Type: text/plain; charset=utf-8');
echo 'Accepted';
wmArchiveFinish($config, $mention['source'] ?? '');
