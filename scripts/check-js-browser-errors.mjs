#!/usr/bin/env node

import puppeteer from 'puppeteer';
import fs from 'fs';
import path from 'path';
import os from 'os';
import toml from 'toml';
import yargs from 'yargs';
import { hideBin } from 'yargs/helpers';
import express from 'express';
import cors from 'cors';

const app = express();

/* Settings */
const urlsFile = 'test-urls.txt';
let testFile = 'test-urls.json';
var configFile = ['config.toml', 'hugo.toml'];
const contentDir = 'docs';
const localPort = 3000;
const ignore404Exact = ['favicon.ico'];
const ignore404Contains = [
  'https://www.youtube.com', 'googleapis.com', 'https://www.youtube-nocookie.com',
  'https://static.doubleclick.net', 'https://i.ytimg.com', 'https://fonts.gstatic.com',
  'https://play.google.com/', 'livereload.js'
];
const waitMs = 30000;
var headless = true;
let additionalBrowserArgs = [];

if (process.env.PUPPETEER_DEBUG) {
  headless = false;
}

const argv = yargs(hideBin(process.argv))
  .option('f', {
    alias: 'force',
    description: 'Don\'t ignore missing files',
    type: 'boolean'
  })
  .option('g', {
    alias: 'gpu',
    description: 'Enable 3D APIs (GPU Emulation)',
    type: 'boolean'
  })
  .option('e', {
    alias: 'experimental',
    description: 'Enable experimental platform features',
    type: 'boolean'
  })
  .option('c', {
    alias: 'config',
    description: 'Test configuration file (JSON)',
    type: 'string'
  })
  .option('l', {
    alias: 'log-server',
    description: 'Log if the internal webserver could fulfill a request',
    type: 'boolean'
  })
  .option('i', {
    alias: 'iiif',
    description: 'Enable IIIF awareness: manifest/info/collection JSON URLs are checked for referenced assets instead of being opened in the browser',
    type: 'boolean'
  })
  .option('css-fail', {
    description: 'Fail the build (exit 128) when undefined CSS classes are found instead of warning only',
    type: 'boolean'
  })
  .option('css-ignore', {
    description: 'Comma separated class names to exclude from the undefined CSS class check',
    type: 'string'
  })
  .help()
  .alias('help', 'h')
  .parse();

if (argv.config) {
  testFile = argv.config;
}

if (!fs.existsSync(contentDir)) {
    console.log('Directory %s doesn\'t exist!', contentDir);
    process.exit(1);
}

let activeConfigFile = null;
for (const cf of configFile) {
  if (fs.existsSync(cf)) {
    activeConfigFile = cf;
    break;
  }
}

if (!activeConfigFile) {
    console.log('Hugo configuration %s doesn\'t exist in current directory (%s), are you sure it contains a Hugo site?', configFile, process.cwd());
    process.exit(2);
}

var tests = [];
var checkMesages = [];
if (fs.existsSync(testFile)) {
    tests = JSON.parse(fs.readFileSync(testFile, 'utf8'));
    if (typeof tests === 'object' && tests !== null && !Array.isArray(tests)) {
        if (tests["messages"]) {
            if (!Array.isArray(tests["messages"])) {
                checkMesages = [tests["messages"]];
            } else {
                checkMesages = tests["messages"];
            }
            delete tests["messages"];
        }
        if (tests.hasOwnProperty('urls')) {
          var tmpTests = [];
          for (const u of tests["urls"]) {
            tmpTests.push({"url": u});
          }
          delete tests["urls"];
          tests = tmpTests;
        }
    }
} else if (fs.existsSync(urlsFile)) {
    var urls = fs.readFileSync(urlsFile).toString().split("\n");
    for (var i in urls) {
        if(urls[i].trim()) tests.push({'url': urls[i]});
    }
} else if (argv.force) {
    console.log('URL file %s doesn\'t exist, exiting!', urlsFile);
    process.exit(3);
} else {
    console.log('File %s not found!', urlsFile);
    tests = [{'url': '/'}];
}

if (argv.experimental) {
  console.log("Enabling experimental platform features");
  additionalBrowserArgs.push('--enable-experimental-web-platform-features');
}

// GPU Emulation Logic
if (!argv.gpu) {
  console.log("Disabling 3D APIs completely");
  additionalBrowserArgs.push('--disable-gpu', '--disable-3d-apis');
} else {
  console.log("Enabling GPU Emulation (SwiftShader/ANGLE)");
  additionalBrowserArgs.push(
    '--use-gl=angle',
    '--use-angle=swiftshader-webgl', // Emulates WebGL using SwiftShader
    '--ignore-gpu-blocklist',
    '--enable-unsafe-swiftshader',
    '--enable-unsafe-webgpu',       // For WebGPU emulation
    '--enable-gpu-rasterization',
    '--enable-accelerated-2d-canvas'
  );
}

const hugoConfig = toml.parse(fs.readFileSync(activeConfigFile).toString());
var baseURL = hugoConfig.baseURL;
const remotePrefix = 'http://localhost:' + localPort + '/';
if (baseURL === '' || !baseURL) {
    baseURL = remotePrefix;
}
// Resources referenced root relative to the base URL's origin (e.g. CSS
// 'url(/fonts/...)' with the fonts convention) don't start with baseURL if
// it contains a path, map them to the local webserver as well
const baseOrigin = new URL(baseURL).origin;
console.log('Base URL is %s', baseURL);

/* IIIF reference checking */
const iiifFileSuffixes = ['manifest.json', 'info.json', 'collection.json'];
const iiifFailures = [];
const iiifCheckedRefs = new Set();
let iiifFilesChecked = 0;
let iiifUrlsChecked = 0;
const iiifAssetExtensions = /\.(jpg|jpeg|png|webp|gif|avif|tif|tiff|jp2|pdf|mp3|mp4|webm)$/i;
const iiifImageRequestPattern = /\/full\/[^/]+\/[^/]+\/[^/]+\.(jpg|jpeg|png|webp|gif|avif|tif|tiff|jp2)$/i;
const localOrigin = new URL(remotePrefix).origin;

/* Undefined CSS class checking
 *
 * Warns about classes used in the rendered DOM but missing from every loaded
 * stylesheet (e.g. purgecss over-purging or template classes without styles).
 * Runs per page after the settle wait, so dynamically injected markup and
 * JS-toggled classes are included. Warn-only unless --css-fail is given.
 */
const cssIgnoreDefault = [
    // Progressive enhancement / JS state hooks that may be unstyled by design
    'no-js', 'js', 'active', 'show', 'hide', 'fail', 'success', 'search-filter-single'
];
const cssIgnore = new Set(cssIgnoreDefault);
if (argv.cssIgnore) {
    for (const name of argv.cssIgnore.split(',')) {
        const trimmed = name.trim();
        if (trimmed) {
            cssIgnore.add(trimmed);
        }
    }
}
const cssFailures = [];
let cssPagesChecked = 0;

// Runs inside the page: classes defined in any loaded stylesheet vs. classes
// used on elements. Recurses into nested grouping rules (media/supports/
// layer/container); cross-origin sheets without cssRules access are skipped.
function cssClassScan(ignoreList) {
    const defined = new Set();
    const re = /\.([A-Za-z_][A-Za-z0-9_-]*)/g;
    const visitRule = (rule) => {
        if (rule.cssRules) {
            for (const child of rule.cssRules) {
                visitRule(child);
            }
        }
        if (rule.selectorText) {
            re.lastIndex = 0;
            let match;
            while ((match = re.exec(rule.selectorText)) !== null) {
                defined.add(match[1]);
            }
        }
    };
    for (const sheet of document.styleSheets) {
        let rules;
        try {
            rules = sheet.cssRules;
        } catch {
            continue;
        }
        if (!rules) {
            continue;
        }
        for (const rule of rules) {
            visitRule(rule);
        }
    }
    const used = new Set();
    for (const element of document.querySelectorAll('[class]')) {
        for (const name of element.classList) {
            if (name) {
                used.add(name);
            }
        }
    }
    const missing = [];
    for (const name of used) {
        if (!defined.has(name) && !ignoreList.includes(name)) {
            missing.push(name);
        }
    }
    return missing.sort();
}

function mapToLocal(url) {
    if (url.startsWith(baseURL)) {
        return remotePrefix + url.slice(baseURL.length);
    }
    if (url.startsWith(baseOrigin)) {
        return remotePrefix.replace(/\/$/, '') + url.slice(baseOrigin.length);
    }
    if (url.startsWith('https://localhost:3000')) {
        return url.replace('https://localhost:3000', 'http://localhost:3000');
    }
    if (url.startsWith('/')) {
        return remotePrefix.replace(/\/$/, '') + url;
    }
    return url;
}

function isAssetRef(pathname) {
    const p = decodeURIComponent(pathname).toLowerCase();
    return iiifAssetExtensions.test(p) || iiifImageRequestPattern.test(p) || p.endsWith('info.json');
}

function isIiifJson(json, kind) {
    if (json === null || typeof json !== 'object') return false;
    const rawContext = json['@context'];
    const context = String(Array.isArray(rawContext) ? rawContext.join(' ') : rawContext || '');
    const type = String(json['type'] || json['@type'] || '');
    if (kind === 'info.json') {
        return /iiif\.io\/api\/image/.test(context) || /iiif\.io\/api\/image/.test(String(json.protocol || ''));
    }
    return /\b(Manifest|Collection)\b/.test(type) || /iiif\.io\/api\/presentation/.test(context);
}

const iiifAssetKeys = new Set(['thumbnail', 'rendering', 'logo', 'seeAlso', 'body']);
function extractAssetRefs(node, collect = false, out = []) {
    if (Array.isArray(node)) {
        for (const item of node) extractAssetRefs(item, collect, out);
        return out;
    }
    if (node !== null && typeof node === 'object') {
        for (const [key, value] of Object.entries(node)) {
            const next = collect || iiifAssetKeys.has(key);
            if (next && (key === 'id' || key === '@id') && typeof value === 'string') {
                out.push(value);
            } else {
                extractAssetRefs(value, next, out);
            }
        }
        return out;
    }
    if (collect && typeof node === 'string' && (node.startsWith('http') || node.startsWith('/'))) {
        out.push(node);
    }
    return out;
}

async function checkIiifRef(ref, source) {
    if (typeof ref !== 'string' || ref === '') return;
    let mapped;
    try {
        mapped = mapToLocal(ref);
    } catch {
        return;
    }
    let parsed;
    try {
        parsed = new URL(mapped);
    } catch {
        return;
    }
    if (parsed.origin !== localOrigin) {
        console.log('[IIIF] Skipping external/non-local reference %s', ref);
        return;
    }
    if (!isAssetRef(parsed.pathname)) {
        console.log('[IIIF] Skipping non-asset reference %s', ref);
        return;
    }
    if (iiifCheckedRefs.has(mapped)) return;
    iiifCheckedRefs.add(mapped);
    iiifUrlsChecked++;
    try {
        const res = await fetch(mapped);
        if (res.status >= 400) {
            iiifFailures.push({ source: source, url: mapped, status: res.status });
            console.log('[IIIF] Missing asset %s (HTTP %d, referenced by %s)', mapped, res.status, source);
        }
    } catch (error) {
        iiifFailures.push({ source: source, url: mapped, status: 0 });
        console.log('[IIIF] Request failed for %s: %s', mapped, error.message);
    }
}

async function checkIiifInfoJson(json, source) {
    const serviceId = json['id'] || json['@id'];
    if (typeof serviceId !== 'string' || serviceId === '') {
        console.log('[IIIF] info.json without id referenced by %s', source);
        return;
    }
    const rawContext = json['@context'];
    const context = String(Array.isArray(rawContext) ? rawContext.join(' ') : rawContext || '');
    const isV3 = context.includes('/image/3') || json.protocol === 'http://iiif.io/api/image/3';
    const sizeWord = isV3 ? 'max' : 'full';
    await checkIiifRef(serviceId + '/full/' + sizeWord + '/0/default.jpg', source);
    for (const size of json.sizes || []) {
        if (size && typeof size.width === 'number' && typeof size.height === 'number') {
            await checkIiifRef(serviceId + '/full/' + size.width + ',' + size.height + '/0/default.jpg', source);
        }
    }
    for (const tile of json.tiles || []) {
        const scaleFactors = Array.isArray(tile.scaleFactors) ? tile.scaleFactors : [];
        const tileWidth = tile.width || 512;
        const tileHeight = tile.height || tileWidth;
        for (const factor of scaleFactors) {
            if (typeof factor !== 'number') continue;
            await checkIiifRef(
                serviceId + '/0,0,' + (tileWidth * factor) + ',' + (tileHeight * factor) + '/' + tileWidth + ',' + tileHeight + '/0/default.jpg',
                source
            );
        }
    }
}

// Use native Node.js temp directory instead of mktemp
const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'puppeteer-'));
const userDir = path.join(tmpDir, 'userdir');
fs.mkdirSync(path.join(userDir, 'Default'), { recursive: true });

const defaultPreferences = {
  plugins: {
    always_open_pdf_externally: true,
  },
};
const prefFile = path.join(userDir, 'Default', 'Preferences');
fs.writeFileSync(prefFile, JSON.stringify(defaultPreferences));
console.log('Wrote preference file to %s', prefFile);

(async () => {
    app.use(cors());
    const webRoot = path.join(process.cwd(), contentDir, '/');

    if (argv.logServer) {
        app.use((req, res, next) => {
            res.on('finish', () => {
                let decodedPath = decodeURIComponent(req.path);
                let resolvedPath = path.join(webRoot, decodedPath);
                let displayPath = resolvedPath;

                try {
                    if (fs.existsSync(resolvedPath)) {
                        const stat = fs.statSync(resolvedPath);
                        if (stat.isDirectory()) {
                            // Directory: check for index.html inside
                            const indexPath = path.join(resolvedPath, 'index.html');
                            if (fs.existsSync(indexPath)) {
                                displayPath = indexPath;
                            } else {
                                displayPath = `${resolvedPath} (directory, no index.html)`;
                            }
                        }
                        // else: it's a file, displayPath is already correct
                    } else {
                        // Path doesn't exist as-is: try appending index.html
                        // (handles URLs like /about that map to /about/index.html)
                        const indexPath = path.join(resolvedPath, 'index.html');
                        if (fs.existsSync(indexPath)) {
                            displayPath = indexPath;
                        } else {
                            displayPath = `${resolvedPath} (not found on disk)`;
                        }
                    }
                } catch (e) {
                    displayPath = `${resolvedPath} (fs error: ${e.message})`;
                }

                if (res.statusCode >= 200 && res.statusCode < 400) {
                    console.log(
                        `[Webserver] %s %s -> %s (HTTP %d)`,
                        req.method,
                        req.url,
                        displayPath,
                        res.statusCode
                    );
                } else {
                    console.log(
                        `[Webserver] %s %s -> NOT FOUND on disk, served from: %s (HTTP %d)`,
                        req.method,
                        req.url,
                        resolvedPath,
                        res.statusCode
                    );
                }
            });
            next();
        });
    }

    app.use(express.static(webRoot));

    const server = app.listen(localPort, function () {
        console.log('Webserver started, serving \'%s\'', webRoot);
    });

    var headlessMode = "shell"; // "shell" is the modern equivalent of "new" headless
    if (!headless) {
      headlessMode = false;
    }

    const browser = await puppeteer.launch({
        headless: headlessMode,
        devtools: false,
        userDataDir: userDir, // Standard way to pass custom profile/preferences
        args: [
            '--no-sandbox',
            '--disable-web-security',
            '--disable-extensions',
            ...additionalBrowserArgs
        ]
    });

    const page = await browser.newPage();
    await page.setRequestInterception(true);

    // Intercept requests
    page.on('request', (request) => { //async 
      const url = request.url();
      try {
        if (page.isClosed() || !request.frame()) {
          //await request.abort('blockedbyclient').catch(() => {});
          console.warn("Request for '%s' was canceled", url);
          return;
        }

        const headers = request.headers();

        // Skip PDFs and livereload
        if (url.toLowerCase().endsWith("pdf")) {
            console.log('Warning: Response would hang Puppeteer, aborting PDF!');
            request.abort();
            return;
        }
        if (url.includes("livereload.js")) {
            console.error('Got request for watcher, this happens if you try to check a development build!');
            request.abort();
            return;
        }

        // ✅ Handle navigation requests: rewrite to localhost
        if (request.isNavigationRequest()) {
            if (url.startsWith(baseURL)) {
                const newUrl = url.replace(baseURL, remotePrefix);
                console.log("Mapping navigation request '%s' to '%s'", url, newUrl);
                request.continue({ url: newUrl, headers });
                return;
            }
            // If not starting with baseURL, let it go
            request.continue();
            return;
        }

        // ✅ Handle resource requests: rewrite to localhost
        if (url.startsWith(baseURL)) {
            const newUrl = url.replace(baseURL, remotePrefix);
            console.log("Mapping resource request '%s' to '%s'", url, newUrl);
            request.continue({ url: newUrl, headers });
            return;
        }

        // Handle requests to the base URL's origin root (e.g. CSS url('/fonts/...'))
        if (!request.isNavigationRequest() && url.startsWith(baseOrigin)) {
            const newUrl = url.replace(baseOrigin, remotePrefix.replace(/\/$/, ''));
            console.log("Mapping origin resource request '%s' to '%s'", url, newUrl);
            request.continue({ url: newUrl, headers });
            return;
        }

        if (url.startsWith("https://localhost:3000")) {
            const newUrl = url.replace("https://localhost:3000", "http://localhost:3000");
            console.log("Mapping resource request '%s' to '%s'", url, newUrl);
            request.continue({ url: newUrl, headers });
            return;
        }

        request.continue();
      } catch {
        console.warn("Request for '%s' was canceled", url);
      }
    });

    page.on('response', response => {
        console.log('Browser: Got response for %s', response.url());
    });

    // EVENT LISTENERS MOVED OUTSIDE THE LOOP TO PREVENT MEMORY LEAKS & DUPLICATE LOGS
    page.on('console', async msg => {
        console.log('Browser console:', msg.text());
        if (msg.text().includes('GPU stall due to ReadPixels')) {
          console.log("Got GPU related error message: " + msg.text());
          page.setDefaultTimeout(60*1000);
        }
        if (checkMesages.length) {
          for (const m of checkMesages) {
            console.log('Checking for "%s"', m);
            if (msg.text().includes(m)) {
              console.log('[console] Failing on message "%s" since it includes "%s"', msg.text(), m);
              if (headless) {
                process.exit(122);
              } else {
                console.log(`Debug mode, waiting ${waitMs}ms before exit`);
                await new Promise(resolve => setTimeout(resolve, waitMs));
                process.exit(122);
              }
            }
          }
        }
    });

    page.on('pageerror', async error => {
        // Page scripts may throw raw strings or objects without a 'message' property
        const message = typeof error === 'string' ? error : (error?.message ?? String(error));
        console.log('[pageerror] "%s"', message);
        if (!argv.gpu && (message.includes('Error creating WebGL context') || message.includes('Unable to create WebGPU adapter'))) {
          console.log(`Ignoring 3D error: ${message}`);
          return;
        }
        if (headless) {
          process.exit(123);
        } else {
          console.log(`Debug mode, waiting ${waitMs}ms before exit`);
          await new Promise(resolve => setTimeout(resolve, waitMs));
          process.exit(123);
        }
    });

    page.on('requestfailed', async request => {
        console.log('[requestfailed] Got error \'%s\' for \'%s\'', request.failure()?.errorText, request.url());
        if (request.resourceType() === 'media') {
            console.log('[requestfailed] Ignoring failed media request for %s', request.url());
        } else {
            const urlPath = request.url().split('?')[0];
            const fileName = urlPath.split('/').pop();

            if (ignore404Exact.includes(fileName) || ignore404Contains.some(v => request.url().includes(v))) {
                console.log('[requestfailed] Ignoring request for %s', request.url());
            } else if (request.url().toLowerCase().endsWith("pdf")) {
                console.log('[requestfailed] Ignoring failed request for PDF file at %s', request.url());
            } else {
              if (headless) {
                process.exit(124);
              } else {
                console.log(`Debug mode, waiting ${waitMs}ms before exit`);
                await new Promise(resolve => setTimeout(resolve, waitMs));
                process.exit(124);
              }
            }
        }
    });

    const checkedUrls = [];
    // Fixed loop iteration
    for (let i = 0; i < tests.length; i++) {
        const testItem = tests[i];
        let localFile = testItem.url || testItem;
        let fragment;

        if (localFile === '/') localFile = 'index.html';
        localFile = localFile.replace(baseURL, '/');

        if (localFile.split("#")[1] !== undefined) {
          fragment = localFile.split("#")[1];
          console.log(`Check for document fragment '${fragment}' requested`);
        }

        localFile = localFile.split("?")[0].split("#")[0];
        if (localFile.startsWith('/')) localFile = localFile.substring(1);

        var checkFile = path.join(process.cwd(), contentDir, localFile);
        if (!argv.force && !fs.existsSync(checkFile)) {
            console.log('Local file %s doesn\'t exist, skipping!', checkFile);
            continue;
        } else if (argv.force && !fs.existsSync(checkFile)) {
            console.log('Local file %s doesn\'t exist, exiting!', checkFile);
            process.exit(3);
        }

        if (argv.iiif) {
            const lower = localFile.toLowerCase();
            const kind = iiifFileSuffixes.find(suffix => lower.endsWith(suffix));
            if (kind) {
                const source = testItem.url || testItem;
                const localUrl = remotePrefix + localFile;
                let status = 0;
                let json = null;
                try {
                    const res = await fetch(localUrl);
                    status = res.status;
                    if (status < 400) {
                        try {
                            json = JSON.parse(await res.text());
                        } catch {
                            json = null;
                        }
                    }
                } catch (error) {
                    console.log('[IIIF] Request failed for %s: %s', localUrl, error.message);
                }
                if (status >= 400) {
                    iiifFailures.push({ source: source, url: localUrl, status: status });
                    console.log('[IIIF] Failed to read %s (HTTP %d)', localUrl, status);
                    continue;
                }
                if (json !== null && isIiifJson(json, kind)) {
                    iiifFilesChecked++;
                    iiifUrlsChecked++;
                    if (kind === 'info.json') {
                        await checkIiifInfoJson(json, source);
                    } else {
                        const refs = [...new Set(extractAssetRefs(json))];
                        for (const ref of refs) {
                            await checkIiifRef(ref, source);
                        }
                    }
                    continue;
                }
                console.log('[IIIF] %s is not IIIF content, checking in browser as usual', source);
            }
        }

        var checkURL = baseURL + localFile;
        if (fragment !== undefined && fragment !== "") {
          checkURL = checkURL + '#' + fragment;
        }
        console.log('-> Opening file %s', checkURL);

        // FIX 1: Always use waitMs as timeout. `timeout: 0` disables Puppeteer's timeout entirely,
        // which can lead to infinite hangs if the page never reaches `networkidle0` (e.g. unclosed sockets).
        let timeout = waitMs;
        console.log(`Opening ${checkURL} with time out ${timeout}`);
        await page.goto(checkURL, { waitUntil: 'networkidle0', timeout: timeout });

        const refreshSelector = "meta[http-equiv=refresh]";
        if (await page.$(refreshSelector) !== null) {
          console.log("Found refresh meta tag, skipping");
          continue;
        }

        if ('click' in testItem) {
            for (let j in testItem['click']) {
                await Promise.all([
                    page.waitForNavigation(),
                    page.click(testItem['click'][j]),
                ]);
            }
        }

        if ('selector' in testItem && 'property' in testItem && 'value' in testItem) {
            // Fixed page.evaluate context error: Pass testItem as argument and return result
            const result = await page.evaluate((cfg) => {
                const element = document.querySelector(cfg.selector);
                if (element !== null) {
                    let style;
                    if ('pseudo' in cfg && cfg.pseudo) {
                        style = getComputedStyle(element, cfg.pseudo);
                    } else {
                        style = getComputedStyle(element);
                    }
                    const actualValue = style.getPropertyValue(cfg.property);
                    return { found: true, actualValue: actualValue, match: actualValue === cfg.value };
                } else {
                    return { found: false };
                }
            }, testItem);

            if (!result.found) {
                console.log('Element for selector \'%s\' not found!', testItem.selector);
                process.exit(126);
            } else if (result.match) {
                console.log('Checking property \'%s\' of %s%s, expected value is \'%s\', actual value is \'%s\'',
                    testItem.property, testItem.selector, testItem.pseudo || '', testItem.value, result.actualValue);
                process.exit(125);
            }
        }

        await new Promise(r => setTimeout(r, 6000));

        // Undefined CSS class check: runs last on the page, after the settle
        // wait, so most JS has loaded and dynamically added classes exist.
        // readyState 'complete' is a safety net for pages that reach
        // networkidle0 before all deferred init has finished.
        try {
            await page.waitForFunction(() => document.readyState === 'complete', { timeout: waitMs });
        } catch {
            console.log('[CSS] readyState never reached \'complete\' on %s, checking anyway', checkURL);
        }
        let undefinedClasses = [];
        try {
            undefinedClasses = await page.evaluate(cssClassScan, [...cssIgnore]);
        } catch (error) {
            console.log('[CSS] Class scan failed for %s: %s', checkURL, error.message);
        }
        cssPagesChecked++;
        if (undefinedClasses.length) {
            const source = testItem.url || testItem;
            cssFailures.push({ url: source, classes: undefinedClasses });
            console.log('[CSS] %d undefined class(es) on %s: %s', undefinedClasses.length, source, undefinedClasses.join(', '));
        } else {
            console.log('[CSS] No undefined classes on %s', testItem.url || testItem);
        }

        checkedUrls.push(testItem.url || testItem);
    }

    if (argv.iiif) {
        console.log('IIIF check: %d files, %d URLs, %d failures', iiifFilesChecked, iiifUrlsChecked, iiifFailures.length);
        for (const failure of iiifFailures) {
            console.log('[IIIF] %s (HTTP %d) referenced by %s', failure.url, failure.status, failure.source);
        }
        if (iiifFailures.length > 0) {
            await browser.close();
            process.exit(127);
        }
    }

    console.log('CSS check: %d page(s) checked, %d page(s) with undefined classes', cssPagesChecked, cssFailures.length);
    for (const failure of cssFailures) {
        console.log('[CSS] %s: %s', failure.url, failure.classes.join(', '));
    }
    if (cssFailures.length > 0) {
        if (argv.cssFail) {
            console.log('Undefined CSS classes found and --css-fail given, exiting with code 128');
            await browser.close();
            process.exit(128);
        }
        console.log('Warning only: rerun with --css-fail to fail the build, or exclude classes with --css-ignore');
    }

    console.log(`Test loop finished, awaiting browser and server to stop, checked ${checkedUrls.join(', ')}`);
    await browser.close();

    // FIX 2: `server.close()` does not close existing keep-alive connections, which can cause
    // the script to hang at the very end waiting for sockets to close. We close it and then force exit.
    server.close();
    setTimeout(() => {
        console.log('Forcing exit as server.close() might be waiting for keep-alive sockets.');
        process.exit(0);
    }, 1000).unref();
})();
