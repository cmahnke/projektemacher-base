<?php
/**
 * Flat file storage for received mentions.
 *
 * One JSON document per (normalized) target page is kept at
 * '<dataDir>/<sha1(target)>.json':
 *
 *   {
 *     "target":   "https://example.org/blog/post/",
 *     "mentions": [ { "source": ..., "type": ..., ... }, ... ]
 *   }
 *
 * Every write goes through wmStoreAtomicWrite (temp file + rename), so
 * concurrent requests can never leave a torn document behind - the
 * storage needs no database and survives rsync deployment.
 */

declare(strict_types=1);

/**
 * Normalizes a URL for comparisons and storage keys: lowercase scheme
 * and host, default ports removed, fragment removed, trailing slash
 * removed except for the bare root.
 */
function wmNormalizeUrl(string $url): ?string
{
    $parts = parse_url($url);
    if ($parts === false || !isset($parts['scheme'], $parts['host'])) {
        return null;
    }
    if (!in_array(strtolower($parts['scheme']), ['http', 'https'], true)) {
        return null;
    }
    $scheme = strtolower($parts['scheme']);
    $host = strtolower($parts['host']);
    if (isset($parts['port'])) {
        $defaultPort = $scheme === 'https' ? 443 : 80;
        if ($parts['port'] !== $defaultPort) {
            $host .= ':' . $parts['port'];
        }
    }
    $path = $parts['path'] ?? '/';
    if ($path !== '/' ) {
        $path = rtrim($path, '/');
        if ($path === '') {
            $path = '/';
        }
    }
    $query = isset($parts['query']) ? '?' . $parts['query'] : '';
    return $scheme . '://' . $host . $path . $query;
}

/** Returns all normalized key variants (with and without trailing slash). */
function wmNormalizeUrlVariants(string $url): array
{
    $normalized = wmNormalizeUrl($url);
    if ($normalized === null) {
        return [];
    }
    $variants = [$normalized];
    if ($normalized !== '/' ) {
        $variants[] = $normalized . '/';
    }
    return array_values(array_unique($variants));
}

/** Storage file path for a target URL. */
function wmStorePath(array $config, string $target): ?string
{
    $normalized = wmNormalizeUrl($target);
    if ($normalized === null) {
        return null;
    }
    return $config['dataDir'] . '/' . sha1($normalized) . '.json';
}

/** Reads the mention document for a target, returns ['target' =>, 'mentions' =>]. */
function wmStoreRead(array $config, string $target): array
{
    $path = wmStorePath($config, $target);
    if ($path === null || !is_file($path)) {
        return ['target' => $target, 'mentions' => []];
    }
    $raw = file_get_contents($path);
    if ($raw === false) {
        return ['target' => $target, 'mentions' => []];
    }
    $doc = json_decode($raw, true);
    if (!is_array($doc) || !isset($doc['mentions']) || !is_array($doc['mentions'])) {
        return ['target' => $target, 'mentions' => []];
    }
    return ['target' => $target, 'mentions' => $doc['mentions']];
}

/**
 * Adds (or updates) a mention for the target. Re-pings from the same
 * source replace the previous entry. Returns true on success.
 */
function wmStoreAdd(array $config, string $target, array $mention): bool
{
    $path = wmStorePath($config, $target);
    if ($path === null || !isset($mention['source'])) {
        return false;
    }
    // Entries are self contained: they carry their target, so they stay
    // valid when moved between documents.
    $mention['target'] = $target;
    $doc = wmStoreRead($config, $target);
    $source = $mention['source'];
    $mentions = array_values(array_filter(
        $doc['mentions'],
        static fn (array $entry): bool => ($entry['source'] ?? null) !== $source
    ));
    $mentions[] = $mention;

    $payload = json_encode(
        ['target' => $target, 'mentions' => $mentions],
        JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT
    );
    if ($payload === false) {
        return false;
    }
    return wmStoreAtomicWrite($path, $payload);
}

/**
 * Atomic write: content goes to a temp file first, then is renamed over
 * the destination, so readers always see a complete document.
 */
function wmStoreAtomicWrite(string $path, string $contents): bool
{
    $dir = dirname($path);
    if (!is_dir($dir) && !mkdir($dir, 0775, true)) {
        return false;
    }
    $tmp = tempnam($dir, 'wm-');
    if ($tmp === false) {
        return false;
    }
    if (file_put_contents($tmp, $contents, LOCK_EX) === false) {
        @unlink($tmp);
        return false;
    }
    if (!rename($tmp, $path)) {
        @unlink($tmp);
        return false;
    }
    return true;
}

/**
 * File based per-IP rate limiting. Returns true while the IP is within
 * the configured limit, false once it exceeded the window.
 */
function wmRateLimitCheck(array $config, string $ip): bool
{
    $limit = $config['rateLimit'];
    $window = $config['rateWindow'];
    if ($limit <= 0 || $window <= 0) {
        return true;
    }
    $bucket = floor(time() / $window);
    $dir = $config['dataDir'] . '/.ratelimit';
    $file = sprintf('%s/%s-%s.count', $dir, sha1($ip), $bucket);
    if (!is_dir($dir) && !mkdir($dir, 0775, true)) {
        // Failing open on a broken storage dir would defeat the purpose,
        // but rejecting everything on a transient error is worse.
        return true;
    }
    $count = 0;
    if (is_file($file)) {
        $count = (int) file_get_contents($file);
    }
    $count++;
    wmStoreAtomicWrite($file, (string) $count);
    return $count <= $limit;
}
