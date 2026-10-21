<?php
/**
 * Configuration for the webmention/pingback collector.
 *
 * Every value can be overridden through an environment variable, which
 * keeps deployments identical across hosts and makes local testing
 * possible without editing this file:
 *
 *   WEBMENTION_ALLOWED_DOMAINS  JSON array of hostnames accepted as
 *                               mention targets (default: example.org)
 *   WEBMENTION_DATA_DIR         storage directory (default: ./data)
 *   WEBMENTION_RATE_LIMIT       max requests per IP per window (default: 20)
 *   WEBMENTION_RATE_WINDOW      rate limit window in seconds (default: 3600)
 *   WEBMENTION_HONEYPOT_FIELD   name of the hidden honeypot form field,
 *                               empty string disables it (default: 'url2')
 *   WEBMENTION_ALLOW_PRIVATE    '1' allows source URLs resolving to
 *                               private/reserved IPs - testing only!
 *   WEBMENTION_ARCHIVE          '1' enables the optional best-effort
 *                               save of mentioned sources at the
 *                               Internet Archive (default: off)
 *   WEBMENTION_ARCHIVE_URL      base URL of the save endpoint,
 *                               'https://web.archive.org/save/'
 *   WEBMENTION_ARCHIVE_ACCESS_KEY  SPN2 API access key (optional);
 *                               when both keys are set the endpoint
 *                               POSTs to the archive API with
 *                               'Authorization: LOW key:secret', when
 *                               unset an anonymous GET on
 *                               '<archiveUrl><source>' is used
 *   WEBMENTION_ARCHIVE_SECRET_KEY  SPN2 API secret key (optional)
 */

declare(strict_types=1);

/**
 * Returns the environment value if set, falls back to the default.
 * Values that look like JSON arrays are decoded, scalars pass through.
 */
function webmentionConfigValue(string $envVar, mixed $default): mixed
{
    $value = getenv($envVar);
    if ($value === false || $value === '') {
        return $default;
    }
    if ($value[0] === '[') {
        $decoded = json_decode($value, true);
        if (is_array($decoded)) {
            return $decoded;
        }
    }
    return $value;
}

return [
    // Hostnames whose URLs are accepted as mention targets. Requests for
    // targets outside this list are rejected (HTTP 400).
    'allowedDomains' => webmentionConfigValue('WEBMENTION_ALLOWED_DOMAINS', ['example.org']),

    // Directory for the per-target JSON documents, created on demand.
    // For nginx hosts (no .htaccess support) point this outside of the
    // document root.
    'dataDir' => webmentionConfigValue('WEBMENTION_DATA_DIR', __DIR__ . '/data'),

    // Simple per-IP rate limiting based on counter files.
    'rateLimit' => (int) webmentionConfigValue('WEBMENTION_RATE_LIMIT', 20),
    'rateWindow' => (int) webmentionConfigValue('WEBMENTION_RATE_WINDOW', 3600),

    // Hidden form field that spam bots fill in. Requests providing it are
    // answered with 202 but silently dropped. Set to '' to disable.
    'honeypotField' => (string) webmentionConfigValue('WEBMENTION_HONEYPOT_FIELD', 'url2'),

    // Testing only: allow source URLs pointing into private networks.
    'allowPrivateIps' => webmentionConfigValue('WEBMENTION_ALLOW_PRIVATE', '') === '1',

    // Optional best-effort archiving of the source URL at the Internet
    // Archive after a mention was stored. Failures are logged and
    // never affect the mention response.
    'archiveEnabled' => webmentionConfigValue('WEBMENTION_ARCHIVE', '') === '1',
    'archiveUrl' => (string) webmentionConfigValue('WEBMENTION_ARCHIVE_URL', 'https://web.archive.org/save/'),
    'archiveAccessKey' => (string) webmentionConfigValue('WEBMENTION_ARCHIVE_ACCESS_KEY', ''),
    'archiveSecretKey' => (string) webmentionConfigValue('WEBMENTION_ARCHIVE_SECRET_KEY', ''),
    'archiveTimeout' => (int) webmentionConfigValue('WEBMENTION_ARCHIVE_TIMEOUT', 15),

    // Limits applied when fetching the source page.
    'fetchTimeout' => 5,
    'fetchMaxBytes' => 1048576,

    // Limits applied to extracted content.
    'maxContentLength' => 500,
];
