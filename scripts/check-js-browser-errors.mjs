#!/usr/bin/env node

import puppeteer from 'puppeteer';
import fs from 'fs';
import path from 'path';
import toml from 'toml';
import yargs from 'yargs';
import { hideBin } from 'yargs/helpers';
import express from 'express';
import cors from 'cors';
import mktemp from 'mktemp';
const app = express();

/* Settings */
const urlsFile = 'test-urls.txt';
let testFile = 'test-urls.json';
var configFile = ['config.toml', 'hugo.toml'];
const contentDir = 'docs'
const localFilePrefix = 'file:./';
const localPort = 3000;
const ignore404Exact = ['favicon.ico'];
const ignore404Contains =['https://www.youtube.com', 'googleapis.com', 'https://www.youtube-nocookie.com', 'https://static.doubleclick.net', 'https://i.ytimg.com', 'https://fonts.gstatic.com', 'https://play.google.com/'];
//const localBaseURLs = ["https://localhost:3000", "http://localhost:3000"];
const waitMs = 20000;
var headless = true;
let additionalBrowserArgs = [];
if (process.env.PUPPETEER_DEBUG) {
  headless = false;
}

const argv = yargs().option('f', {
    alias: 'force',
    description: 'Don\'t ignore mising files',
    type: 'boolean'
  })
  .option('g', {
    alias: 'gpu',
    description: 'Enable 3D Apis',
    type: 'boolean'
  })
  .option('e', {
    alias: 'experimental',
    description: 'Enable experimental plattform features',
    type: 'boolean'
  })
  .option('c', {
    alias: 'config',
    description: 'Configuration file',
    type: 'string'
  })
  .help()
  .alias('help', 'h').parse(hideBin(process.argv));

if (argv.config) {
  testFile = argv.config
}

if (!fs.existsSync(contentDir)) {
    console.log('Directory %s doesn\'t exist!', contentDir);
    process.exit(1);
}

for (const cf of configFile) {
  if (fs.existsSync(cf)) {
    configFile = cf;
    break;
  }
}

if (!fs.existsSync(configFile)) {
    console.log('Hugo configuration %s doesn\'t exist in current directory (%s), are you sure, it\'s containig a Hugo site?', configFile, process.cwd());
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
        tests.push({'url': urls[i]});
    }
} else if (argv.force) {
    console.log('URL file %s doesn\'t exist, exiting!', urlsFile);
    process.exit(3);
} else {
    console.log('File %s not found!', urlsFile);
    urls = ['/'];
}

if (argv.experimental) {
  console.log("Enabling experimental plattform features");
  additionalBrowserArgs = ['--enable-experimental-web-platform-features'];
}
if (!argv.gpu) {
  console.log("Disabling 3D APIs");
  additionalBrowserArgs = [...additionalBrowserArgs, '--disable-gpu']; //--disable-3d-apis
} else {
  console.log("Enable unsafe shader");
  additionalBrowserArgs = [...additionalBrowserArgs, '--enable-unsafe-swiftshader', '--enable-unsafe-webgpu'];
}

const hugoConfig = toml.parse(fs.readFileSync(configFile).toString());
var baseURL = hugoConfig.baseURL;
const remotePrefix = 'http://localhost:' + localPort + '/';
if (baseURL == '') {
    baseURL = remotePrefix
}
console.log('Base URL is %s', baseURL);

/*
  See https://bugs.chromium.org/p/chromium/issues/detail?id=761295
  See https://github.com/microsoft/playwright/issues/3509#issuecomment-675441299
*/
const tmpDir = mktemp.createDirSync('XXX-XXX');
fs.mkdirSync(`${tmpDir}/userdir/Default`, { recursive: true });

const defaultPreferences = {
  plugins: {
    always_open_pdf_externally: true,
  },
}
const prefFile = `${tmpDir}/userdir/Default/Preferences`;
fs.writeFileSync(prefFile, JSON.stringify(defaultPreferences));
console.log('Wrote preference file to %s', prefFile);

(async () => {

    app.use(cors());
    const webRoot = path.join(process.cwd(), contentDir, '/');
    /* TODO: This behaves differently then GitHub, redirect to URL ending in slash on request on directories. */
    app.use(express.static(webRoot));
    var server = app.listen(localPort, function () {
        console.log('Webserver started, serving \'%s\'', webRoot);
    });

    var headlessMode = "new";
    if (!headless) {
      headlessMode = 'false';
    }

    const browser = await puppeteer.launch ({
        /*userDataDir: path.resolve(__dirname, './puppeteerTmp'),*/
        /*  https://developer.chrome.com/articles/new-headless/
        headless: true,
        */
        headless: headlessMode,
        devtools: false,
        //'--allow-running-insecure-content',
        args:['--use-gl=egl', '--no-sandbox', '--disable-web-security', `--initial-preferences-file="${prefFile}"`, ...additionalBrowserArgs]
         /* '--disable-web-security', '--allow-failed-policy-fetch-for-test', '--allow-running-insecure-content', '--unsafely-treat-insecure-origin-as-secure=' + baseURL] */
    })
    const page = await browser.newPage();
    await page.setRequestInterception(true);

    page.on('request', request => {
        const headers = request.headers();
        var newRequestUrl;
        if (request.url().toLowerCase().endsWith("pdf")) {
          console.log('Warning: Response would hang Puppeteer, aborting!');
          request.abort();
          return;
        }
        if (request.url().includes("livereload.js")) {
          console.error('Got request for watcher, this happens if you try to check a development build!');
          request.abort();
          return;
        }
        if (request.url().startsWith(baseURL)) {
            newRequestUrl = request.url().replace(baseURL, remotePrefix)
            console.log("Mapping request for '%s' to '%s'", request.url(), newRequestUrl);
            request.continue({
                url: newRequestUrl,
                headers : headers
            });
            return;
        }
        if (request.url().startsWith("https://localhost:3000")) {
            newRequestUrl = request.url().replace("https://localhost:3000", "http://localhost:3000")
            console.log("Mapping request for '%s' to '%s'", request.url(), newRequestUrl);
            request.continue({
                url: newRequestUrl,
                headers : headers
            });
            return;
        }
        request.continue();
        })
        .on('response', response => {
            console.log('Browser: Got response for %s', response.url());
        });

    const checkedUrls = [];
    for (var i in tests) {
        var localFile, fragment;
        if (typeof tests[i] === 'object' && tests[i] !== null && tests[i].hasOwnProperty('url')) {
            localFile = tests[i]['url'];
        } else {
            localFile = tests[i];
        }
        if (localFile == '/') {
            localFile = 'index.html';
        }
        localFile = localFile.replace(baseURL, '/')
        if (localFile.split("#")[1] !== undefined) {
          fragment = localFile.split("#")[1]
          console.log(`Check for document fragment '${fragment}' requested`);
        }
        localFile = localFile.split("?")[0].split("#")[0]
        if (localFile.startsWith('/')) {
            localFile = localFile.substring(1);
        }

        var checkFile = path.join(process.cwd(),  contentDir, localFile)
        if (!argv.force && !fs.existsSync(checkFile)) {
            console.log('Local file %s doesn\'t exist, skipping!', checkFile);
            continue;
        } else if (argv.force && !fs.existsSync(checkFile)) {
            console.log('Local file %s doesn\'t exist, exiting!', checkFile);
            process.exit(3);
        }
        //var response;
        page.on('console', msg => {
            console.log('Browser console:', msg.text());
            if (msg.text().includes('GPU stall due to ReadPixels')) {
              console.log("Got GPU relateted error message: " + msg.text())
              page.setDefaultTimeout(60*1000);
              /*
              setTimeout(() => {

              }, 60*1000)
              */
            }
            if (checkMesages.length) {
              for (const m of checkMesages) {
                console.log('Checking for "%s"', m);
                if (msg.text().includes(m)) {
                  console.log('[console] Failing on message "%s" since it includes "%s"', msg.text(), m);
                  if (headless) {
                    process.exit(122);
                  } else {
                    setTimeout(() => {
                      console.log(`Debug mode, waiting ${waitMs}ms instead of exit`)
                    }, waitMs)
                  }
                }
              }
            }
          })
          .on('pageerror', error => {
            console.log('[pageerror] "' + error.message + '" on path / file:', localFile);
            if (!argv.gpu && (error.message.includes('Error creating WebGL context') || error.message.includes('Unable to create WebGPU adapter'))) {
              console.log(`Ignoring 3D error: ${error.message}`)
              return
            }
            if (headless) {
              process.exit(123);
            } else {
              setTimeout(() => {
                console.log(`Debug mode, waiting ${waitMs}ms instead of exit`)
              }, waitMs)
            }
          })
          .on('requestfailed', request => {
            console.log('[requestfailed] Got error \'%s\' for \'%s\'', request.failure().errorText, request.url());
            if (request.resourceType() == 'media') {
                console.log('[requestfailed] Ignoring failed media request for %s', request.url());
            } else if (ignore404Exact.includes(request.url().split('/')[-1]) || ignore404Contains.some(v => request.url().includes(v))) {
                console.log('[requestfailed] Ignoring request for %s', request.url());
            } else if (request.url().toLowerCase().endsWith("pdf")) {
                console.log('[requestfailed] Ignoring failed request for PDF file at %s', request.url());
            } else {
              if (headless) {
                process.exit(124);
              } else {
                setTimeout(() => {
                  console.log(`Debug mode, waiting ${waitMs}ms instead of exit`)
                }, waitMs)
              }
            }
        });

        var checkURL = baseURL + localFile;
        if (fragment !== undefined && fragment != "") {
          checkURL = checkURL + '#' + fragment;
        }
        console.log('-> Opening file %s', checkURL);
        let timeout = 0;
        if (argv.gpu) {
          timeout = waitMs;
        }
        console.log(`Opening ${checkURL} with time out ${timeout}`);
        const open = await page.goto(checkURL, { waitUntil: 'networkidle0', timeout: timeout });

        const refreshSelector = "meta[http-equiv=refresh]";
        if (await page.$(refreshSelector) !== null) {
          console.log("Found refresh meta tag, skipping");
          continue;
        }

        if ('click' in tests[i]) {
            for (let j in tests[i]['click']) {
                const [response] = await Promise.all([
                    page.waitForNavigation(),
                    page.click(tests[i]['click'][j]),
                ]);
            }
        }

        if ('selector' in tests[i] && 'property' in tests[i] && 'value' in tests[i]) {
            page.evaluate(() => {
                const element = document.querySelector(tests[i]['selector']);
                if (element !== null) {
                    var style;
                    if ('pseudo' in tests[i]) {
                        style = getComputedStyle(element, tests[i]['pseudo'])
                    } else {
                        style = getComputedStyle(element);
                        tests[i]['pseudo'] = '';
                    }
                    const actualValue = style.getPropertyValue(tests[i]['property'])
                    if (actualValue == tests[i]['value']) {
                        console.log('Checking poperty \'%s\' of %s%s, expected value is \'%s\', actual value is \'%s\'', tests[i]['property'], tests[i]['selector'], tests[i]['pseudo'], tests[i]['value'], actualValue);
                        process.exit(125);
                    }
                  } else {
                    console.log('Element for selector \'%s\' not found!', tests[i]['selector'])
                    process.exit(126);
                  }
            });
        }

        //Events doen't really work well, just wait :(
        //await page.waitForTimeout(5000);
        await new Promise(r => setTimeout(r, 6000));
        //await page.waitForNavigation();
        checkedUrls.push(tests[i]['url'])
    }
    console.log(`Test loop finished, awaiting browser and server to stop, checked ${checkedUrls.join(', ')}`)
    await browser.close();
    await server.close();
})();
