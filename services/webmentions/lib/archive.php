<?php
/**
 * Optional best-effort archiving of mentioned source pages at the
 * Internet Archive (Save Page Now).
 *
 * Runs after the mention response was released (fastcgi_finish_request
 * when available). The whole thing is fire-and-forget: transport
 * failures, HTTP errors and rate limits are written to the server
 * error log and swallowed - a failed archive save never invalidates
 * an accepted mention.
 *
 * Modes (see config.php):
 * - SPN2 credentials set: POST to the save API with
 *   'Authorization: LOW <access>:<secret>'.
 * - otherwise: anonymous GET on '<archiveUrl><source>'.
 */

declare(strict_types=1);

/**
 * Performs one archive request. Returns the final HTTP status code
 * (after redirects) or null on any transport failure; errors are
 * logged, never thrown.
 */
function wmArchiveRequest(
    string $url,
    string $method,
    array $headers,
    ?string $body,
    int $timeout
): ?int {
    if (function_exists('curl_init')) {
        $handle = curl_init($url);
        if ($handle === false) {
            return null;
        }
        curl_setopt_array($handle, [
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_CUSTOMREQUEST => $method,
            CURLOPT_HTTPHEADER => $headers,
            CURLOPT_FOLLOWLOCATION => true,
            CURLOPT_MAXREDIRS => 3,
            CURLOPT_TIMEOUT => $timeout,
            CURLOPT_CONNECTTIMEOUT => $timeout,
            CURLOPT_USERAGENT => 'webmention-archiver/0.1',
            CURLOPT_PROTOCOLS => CURLPROTO_HTTP | CURLPROTO_HTTPS,
        ]);
        if ($body !== null) {
            curl_setopt($handle, CURLOPT_POSTFIELDS, $body);
        }
        curl_exec($handle);
        $errorNumber = curl_errno($handle);
        $errorMessage = curl_error($handle);
        $status = (int) curl_getinfo($handle, CURLINFO_RESPONSE_CODE);
        if ($errorNumber !== 0) {
            error_log("webmention archive: curl error $errorNumber ($errorMessage) fetching $url");
            return null;
        }
        return $status;
    }
    // Stream fallback (no curl extension).
    $streamOptions = [
        'method' => $method,
        'timeout' => $timeout,
        'follow_location' => 1,
        'max_redirects' => 3,
        'user_agent' => 'webmention-archiver/0.1',
        'ignore_errors' => true,
    ];
    if ($body !== null) {
        $streamOptions['content'] = $body;
    }
    if ($headers !== []) {
        $streamOptions['header'] = implode("\r\n", $headers);
    }
    $context = stream_context_create([
        'http' => $streamOptions,
        'ssl' => ['verify_peer' => true],
    ]);
    @file_get_contents($url, false, $context);
    // The last header line carries the final (after redirects) status.
    $status = null;
    foreach (array_reverse($http_response_header ?? []) as $line) {
        if (preg_match('#^HTTP/[\d.]+ (\d{3})#', $line, $matches) === 1) {
            $status = (int) $matches[1];
            break;
        }
    }
    if ($status === null) {
        error_log("webmention archive: no HTTP response for $url");
        return null;
    }
    return $status;
}

/**
 * Sends the mentioned source URL to the Internet Archive. Does
 * nothing when archiving is not enabled; every outcome - accepted or
 * failed - only lands in the server error log.
 */
function wmArchiveSave(array $config, string $sourceUrl): void
{
    if (empty($config['archiveEnabled'])) {
        return;
    }
    // Fall back to the documented defaults so a stale or hand-edited
    // config.php cannot break the call.
    $config += [
        'archiveUrl' => 'https://web.archive.org/save/',
        'archiveTimeout' => 15,
    ];
    $base = rtrim((string) ($config['archiveUrl'] ?? ''), '/');
    $accessKey = (string) ($config['archiveAccessKey'] ?? '');
    $secretKey = (string) ($config['archiveSecretKey'] ?? '');
    $timeout = (int) $config['archiveTimeout'];
    if (($accessKey !== '') !== ($secretKey !== '')) {
        error_log('webmention archive: WEBMENTION_ARCHIVE_ACCESS_KEY and WEBMENTION_ARCHIVE_SECRET_KEY'
            . ' must both be set for credentialed saves - falling back to anonymous');
    }
    try {
        $status = null;
        if ($accessKey !== '' && $secretKey !== '') {
            // SPN2 API: create a save job, the archive does the rest.
            $status = wmArchiveRequest(
                $base . '/',
                'POST',
                [
                    'Authorization: LOW ' . $accessKey . ':' . $secretKey,
                    'Content-Type: application/x-www-form-urlencoded',
                ],
                http_build_query(['url' => $sourceUrl, 'skip_first_archive' => '1']),
                $timeout
            );
        } else {
            $status = wmArchiveRequest(
                $base . '/' . $sourceUrl,
                'GET',
                [],
                null,
                $timeout
            );
        }
        if ($status === null) {
            error_log("webmention archive: transport failure saving $sourceUrl");
        } elseif ($status < 200 || $status >= 400) {
            error_log("webmention archive: HTTP $status saving $sourceUrl");
        } else {
            error_log("webmention archive: accepted $sourceUrl (HTTP $status)");
        }
    } catch (Throwable $exception) {
        error_log('webmention archive: ' . $exception->getMessage() . " saving $sourceUrl");
    }
}
