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
const localFilePrefix = 'file:./';
const localPort = 3000;
const ignore404Exact = ['favicon.ico'];
const ignore404Contains = [
  'https://www.youtube.com', 'googleapis.com', 'https://www.youtube-nocookie.com',
  'https://static.doubleclick.net', 'https://i.ytimg.com', 'https://fonts.gstatic.com',
  'https://play.google.com/', 'livereload.js'
];
const waitMs = 20000;
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
console.log('Base URL is %s', baseURL);

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
            ...additionalBrowserArgs
        ]
    });

    const page = await browser.newPage();
    await page.setRequestInterception(true);

    // Intercept requests
    page.on('request', request => {
        const headers = request.headers();
        let newRequestUrl;

        if (request.url().toLowerCase().endsWith("pdf")) {
          console.log('Warning: Response would hang Puppeteer, aborting PDF!');
          request.abort();
          return;
        }
        if (request.url().includes("livereload.js")) {
          console.error('Got request for watcher, this happens if you try to check a development build!');
          request.abort();
          return;
        }
        if (request.url().startsWith(baseURL)) {
            newRequestUrl = request.url().replace(baseURL, remotePrefix);
            console.log("Mapping request for '%s' to '%s'", request.url(), newRequestUrl);
            request.continue({ url: newRequestUrl, headers: headers });
            return;
        }
        if (request.url().startsWith("https://localhost:3000")) {
            newRequestUrl = request.url().replace("https://localhost:3000", "http://localhost:3000");
            console.log("Mapping request for '%s' to '%s'", request.url(), newRequestUrl);
            request.continue({ url: newRequestUrl, headers: headers });
            return;
        }
        request.continue();
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
        console.log('[pageerror] "' + error.message + '" on path / file:', error);
        if (!argv.gpu && (error.message.includes('Error creating WebGL context') || error.message.includes('Unable to create WebGPU adapter'))) {
          console.log(`Ignoring 3D error: ${error.message}`);
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
            // Fixed Python syntax error: split('/')[-1]
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

        var checkURL = baseURL + localFile;
        if (fragment !== undefined && fragment !== "") {
          checkURL = checkURL + '#' + fragment;
        }
        console.log('-> Opening file %s', checkURL);

        let timeout = argv.gpu ? waitMs : 0;
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
        checkedUrls.push(testItem.url || testItem);
    }

    console.log(`Test loop finished, awaiting browser and server to stop, checked ${checkedUrls.join(', ')}`);
    await browser.close();
    await new Promise(resolve => server.close(resolve)); // Properly await server closure
})();
