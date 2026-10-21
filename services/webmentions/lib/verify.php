<?php
/**
 * Source verification and content extraction for incoming mentions.
 *
 * Implements the heart of the webmention protocol: fetching the source
 * page (with strict size/time limits and an SSRF guard) and checking
 * that it really links to the mentioned target. Basic microformats
 * (h-entry/h-card) are extracted to give the mention a type, an author
 * and some content - gracefully falling back to <title>/meta author.
 */

declare(strict_types=1);

/** Syntactic URL check: http(s) and a host are required. */
function wmUrlValid(string $url): bool
{
    $parts = parse_url($url);
    if ($parts === false || !isset($parts['scheme'], $parts['host'])) {
        return false;
    }
    if (!in_array(strtolower($parts['scheme']), ['http', 'https'], true)) {
        return false;
    }
    return filter_var($url, FILTER_VALIDATE_URL) !== false;
}

/**
 * SSRF guard: rejects hosts that resolve into private or reserved IP
 * ranges (loopback, RFC1918, link-local, ...).
 */
function wmUrlIsPublic(string $url, array $config): bool
{
    if ($config['allowPrivateIps']) {
        return true;
    }
    $host = parse_url($url, PHP_URL_HOST);
    if (!is_string($host) || $host === '') {
        return false;
    }
    $ip = filter_var($host, FILTER_VALIDATE_IP);
    if ($ip === false) {
        $ip = gethostbyname($host);
        if ($ip === $host) {
            return false; // unresolvable
        }
    }
    return filter_var($ip, FILTER_VALIDATE_IP, FILTER_FLAG_NO_PRIV_RANGE | FILTER_FLAG_NO_RES_RANGE) !== false;
}

/**
 * Fetches a URL with hard time and size limits. Uses curl when
 * available and falls back to stream wrappers, following up to five
 * redirects. Returns the body and the final HTTP status code, or null
 * on any transport failure.
 *
 * @return array{body: string, status: ?int}|null
 */
function wmFetchUrl(string $url, array $config): ?array
{
    $timeout = $config['fetchTimeout'];
    $maxBytes = $config['fetchMaxBytes'];
    if (function_exists('curl_init')) {
        $handle = curl_init($url);
        if ($handle === false) {
            return null;
        }
        curl_setopt_array($handle, [
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_FOLLOWLOCATION => true,
            CURLOPT_MAXREDIRS => 5,
            CURLOPT_TIMEOUT => $timeout,
            CURLOPT_CONNECTTIMEOUT => $timeout,
            CURLOPT_USERAGENT => 'webmention-verifier/0.1',
            CURLOPT_PROTOCOLS => CURLPROTO_HTTP | CURLPROTO_HTTPS,
        ]);
        $body = curl_exec($handle);
        $transportOk = curl_errno($handle) === 0;
        $status = curl_getinfo($handle, CURLINFO_RESPONSE_CODE);
        if (!$transportOk) {
            error_log('webmention verify: curl transport error fetching ' . $url);
        }
        if (!$transportOk || !is_string($body)) {
            return null;
        }
        return ['body' => mb_substr($body, 0, $maxBytes), 'status' => (int) $status];
    }
    $context = stream_context_create([
        'http' => [
            'timeout' => $timeout,
            'follow_location' => 1,
            'max_redirects' => 5,
            'user_agent' => 'webmention-verifier/0.1',
        ],
        'ssl' => ['verify_peer' => true],
    ]);
    $body = @file_get_contents($url, false, $context, 0, $maxBytes);
    if ($body === false) {
        return null;
    }
    // The last header line from $http_response_header carries the
    // final (after redirects) status code.
    $status = null;
    foreach (array_reverse($http_response_header ?? []) as $line) {
        if (preg_match('#^HTTP/[\d.]+ (\d{3})#', $line, $matches) === 1) {
            $status = (int) $matches[1];
            break;
        }
    }
    return ['body' => $body, 'status' => $status];
}

/** Resolves a possibly relative URL against the source document URL. */
function wmResolveUrl(string $relative, string $base): ?string
{
    $relative = trim($relative);
    if ($relative === '') {
        return null;
    }
    if (preg_match('/^https?:\/\//i', $relative)) {
        return $relative;
    }
    $parts = parse_url($base);
    if ($parts === false || !isset($parts['scheme'], $parts['host'])) {
        return null;
    }
    $scheme = strtolower($parts['scheme']);
    $root = $scheme . '://' . strtolower($parts['host']);
    if (isset($parts['port'])) {
        $defaultPort = $scheme === 'https' ? 443 : 80;
        if ($parts['port'] !== $defaultPort) {
            $root .= ':' . $parts['port'];
        }
    }
    if (str_starts_with($relative, '//')) {
        return $scheme . ':' . $relative;
    }
    if (str_starts_with($relative, '/')) {
        return $root . $relative;
    }
    if (preg_match('/^[a-z][a-z0-9+.-]*:/i', $relative)) {
        return null; // other schemes (mailto:, ...) never match an http target
    }
    $path = $parts['path'] ?? '/';
    $dir = substr($path, 0, (int) strrpos($path, '/') + 1);
    return $root . $dir . $relative;
}

/**
 * Checks that the source document links to the target. URL comparison
 * runs on normalized variants (scheme/host case, trailing slash,
 * fragments and default ports ignored) over href/src/cite/poster
 * attribute values; falls back to a raw substring search.
 */
function wmFindBacklink(string $html, string $source, string $target): bool
{
    $candidates = wmNormalizeUrlVariants($target);
    if ($candidates === []) {
        return false;
    }
    $document = new DOMDocument();
    libxml_use_internal_errors(true);
    $loaded = $document->loadHTML(
        '<?xml encoding="utf-8"?>' . $html,
        LIBXML_NOWARNING | LIBXML_NOERROR
    );
    libxml_clear_errors();
    if ($loaded) {
        $xpath = new DOMXPath($document);
        foreach (['a', 'img', 'video', 'audio', 'link', 'cite'] as $tag) {
            $nodes = $xpath->query('//' . $tag);
            if ($nodes === false) {
                continue;
            }
            foreach ($nodes as $node) {
                if (!$node instanceof DOMElement) {
                    continue;
                }
                foreach (['href', 'src', 'cite', 'poster'] as $attribute) {
                    $value = $node->getAttribute($attribute);
                    if ($value === '') {
                        continue;
                    }
                    $resolved = wmResolveUrl($value, $source);
                    if ($resolved === null) {
                        continue;
                    }
                    $normalized = wmNormalizeUrl($resolved);
                    if ($normalized !== null && in_array($normalized, $candidates, true)) {
                        return true;
                    }
                }
            }
        }
    }
    // Fallback: raw substring search over common HTML encodings.
    $haystack = html_entity_decode($html, ENT_QUOTES | ENT_HTML5, 'UTF-8');
    foreach ($candidates as $candidate) {
        if (str_contains($html, $candidate) || str_contains($haystack, $candidate)) {
            return true;
        }
    }
    return false;
}

/**
 * Extracts mention metadata from the source document using basic
 * microformats class matching (h-entry, p-name, p-content, p-author,
 * u-like-of, u-repost-of, u-in-reply-to). Returns the entry skeleton
 * that wmStoreAdd persists.
 */
function wmExtractEntry(string $html, string $source, string $type, array $config): array
{
    $entry = [
        'source' => $source,
        'type' => $type,
        'received' => gmdate('Y-m-d\TH:i:s\Z'),
    ];
    $document = new DOMDocument();
    libxml_use_internal_errors(true);
    $loaded = $document->loadHTML(
        '<?xml encoding="utf-8"?>' . $html,
        LIBXML_NOWARNING | LIBXML_NOERROR
    );
    libxml_clear_errors();
    if (!$loaded) {
        return $entry;
    }
    $xpath = new DOMXPath($document);
    $hasClass = static function (DOMElement $element, string $class): bool {
        return in_array($class, explode(' ', $element->getAttribute('class')), true);
    };

    $hEntry = null;
    $entries = $xpath->query('//*[contains(concat(" ", normalize-space(@class), " "), " h-entry ")]');
    if ($entries !== false && $entries->length > 0) {
        $first = $entries->item(0);
        if ($first instanceof DOMElement) {
            $hEntry = $first;
        }
    }

    // Title: p-name inside the h-entry, otherwise <title>.
    $title = null;
    if ($hEntry !== null) {
        // Type detection: the first matching u-* relationship class
        // wins (like/repost/bookmark/reply), otherwise the passed
        // default ('mention' or 'pingback') is kept.
        foreach ([
            'u-like-of' => 'like',
            'u-repost-of' => 'repost',
            'u-bookmark-of' => 'bookmark',
            'u-in-reply-to' => 'reply',
        ] as $relationClass => $detectedType) {
            $relationNode = wmClassNode($xpath, $hEntry, $relationClass);
            if ($relationNode !== null) {
                $entry['type'] = trim($detectedType);
                break;
            }
        }
        $title = wmClassValue($xpath, $hEntry, 'p-name');
    }
    if ($title === null || trim($title) === '') {
        $titles = $xpath->query('//title');
        $title = ($titles !== false && $titles->length > 0) ? $titles->item(0)->textContent : null;
    }
    $title = wmSanitizeText((string) $title, 300);
    if ($title !== '') {
        $entry['title'] = $title;
    }

    // Content: p-content, then p-summary.
    $content = null;
    if ($hEntry !== null) {
        foreach (['p-content', 'p-summary'] as $contentClass) {
            $content = wmClassValue($xpath, $hEntry, $contentClass);
            if ($content !== null && trim($content) !== '') {
                break;
            }
        }
    }
    $content = wmSanitizeText((string) $content, (int) $config['maxContentLength']);
    if ($content !== '') {
        $entry['content'] = $content;
    }

    // Author: p-author/h-card inside (or around) the h-entry, falling
    // back to <meta name="author">.
    $author = [];
    $scope = $hEntry;
    $authorNode = null;
    while ($scope !== null && $authorNode === null) {
        $nodes = $xpath->query(
            './/*[contains(concat(" ", normalize-space(@class), " "), " p-author ")]',
            $scope
        );
        if ($nodes !== false && $nodes->length > 0) {
            $item = $nodes->item(0);
            if ($item instanceof DOMElement) {
                $authorNode = $item;
            }
        }
        $scope = $scope->parentNode instanceof DOMElement ? $scope->parentNode : null;
    }
    if ($authorNode === null) {
        $cards = $xpath->query('//*[contains(concat(" ", normalize-space(@class), " "), " h-card ")]');
        if ($cards !== false && $cards->length > 0) {
            $item = $cards->item(0);
            if ($item instanceof DOMElement) {
                $authorNode = $item;
            }
        }
    }
    if ($authorNode !== null) {
        $name = wmSanitizeText($authorNode->textContent, 200);
        if ($name !== '') {
            $author['name'] = $name;
        }
        $urls = $xpath->query(
            './/*[contains(concat(" ", normalize-space(@class), " "), " u-url ")]',
            $authorNode
        );
        if ($urls !== false && $urls->length > 0) {
            $item = $urls->item(0);
            if ($item instanceof DOMElement) {
                $url = trim($item->getAttribute('href'));
                if (wmUrlValid($url)) {
                    $author['url'] = $url;
                }
            }
        }
    }
    if (!isset($author['name'])) {
        $metaAuthors = $xpath->query('//meta[@name="author"][@content]');
        if ($metaAuthors !== false && $metaAuthors->length > 0) {
            $item = $metaAuthors->item(0);
            if ($item instanceof DOMElement) {
                $name = wmSanitizeText($item->getAttribute('content'), 200);
                if ($name !== '') {
                    $author['name'] = $name;
                }
            }
        }
    }
    if ($author !== []) {
        $entry['author'] = $author;
    }

    return $entry;
}

/** First element with the given microformats class inside a scope. */
function wmClassNode(DOMXPath $xpath, DOMElement $scope, string $class): ?DOMElement
{
    $nodes = $xpath->query(
        './/*[contains(concat(" ", normalize-space(@class), " "), " ' . $class . ' ")]',
        $scope
    );
    if ($nodes === false || $nodes->length === 0) {
        return null;
    }
    $node = $nodes->item(0);
    return $node instanceof DOMElement ? $node : null;
}

/** First text content of an element with the given microformats class. */
function wmClassValue(DOMXPath $xpath, DOMElement $scope, string $class): ?string
{
    $nodes = $xpath->query(
        './/*[contains(concat(" ", normalize-space(@class), " "), " ' . $class . ' ")]',
        $scope
    );
    if ($nodes === false || $nodes->length === 0) {
        return null;
    }
    return $nodes->item(0)->textContent;
}

/**
 * Reduces text to plain, single-line output: tags stripped, entities
 * decoded, whitespace collapsed, hard length cap.
 */
function wmSanitizeText(string $text, int $limit): string
{
    $text = strip_tags($text);
    $text = html_entity_decode($text, ENT_QUOTES | ENT_HTML5, 'UTF-8');
    $text = preg_replace('/\s+/u', ' ', $text) ?? '';
    $text = trim($text);
    if (function_exists('mb_substr')) {
        return mb_substr($text, 0, $limit);
    }
    return substr($text, 0, $limit);
}
