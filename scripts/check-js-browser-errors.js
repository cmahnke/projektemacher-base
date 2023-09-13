const puppeteer = require ('puppeteer')
const fs = require('fs');
const path = require('path');
const toml = require('toml');
const yargs = require('yargs');
const express = require('express');
const cors = require('cors');
const mktemp = require('mktemp');
const app = express();


/* Settings */
const urlsFile = 'test-urls.txt';
const testFile = 'test-urls.json';
const configFile = 'config.toml';
const contentDir = 'docs'
const localFilePrefix = 'file:./';
const localPort = 3000;
const ignore404Exact = ['favicon.ico'];
const ignore404Contains =['https://www.youtube.com', 'googleapis.com', 'https://www.youtube-nocookie.com', 'https://static.doubleclick.net', 'https://i.ytimg.com', 'https://fonts.gstatic.com'];

const argv = yargs.option('force', {
    alias: 'f',
    description: 'Don\'t ignore mising files',
    type: 'boolean'
  })
  .help()
  .alias('help', 'h').argv;

if (!fs.existsSync(contentDir)) {
    console.log('Directory %s doesn\'t exist!', contentDir);
    process.exit(1);
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

    const browser = await puppeteer.launch ({
        /*userDataDir: path.resolve(__dirname, './puppeteerTmp'),*/
        /*  https://developer.chrome.com/articles/new-headless/
        headless: true,
        */
        headless: 'new',
        devtools: false,
        args:['--use-gl=egl', '--disable-web-security', `--initial-preferences-file="${prefFile}"`]
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
        request.continue();
        })
        .on('response', response => {
            console.log('Browser: Got response for %s', response.url());
        });

    for (var i in tests) {
        var localFile;
        if (typeof tests[i] === 'object' && tests[i] !== null && tests[i].hasOwnProperty('url')) {
            localFile = tests[i]['url'];
        } else {
            localFile = tests[i];
        }
        if (localFile == '/') {
            localFile = 'index.html';
        }
        localFile = localFile.replace(baseURL, '/')
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
              if (checkMesages.length) {
                for (const m of checkMesages) {
                  console.log('Checking for "%s"', m);
                  if (msg.text().includes(m)) {
                    console.log('[console] Failing on message %s since it includes "%s"', msg.text(), m);
                    process.exit(122);
                  }
                }
              }
            })
            .on('pageerror', error => {
              console.log('[pageerror] ' + error.message);
              process.exit(123);
            })
            .on('requestfailed', request => {
              console.log('[requestfailed] Got error \'%s\' for \'%s\'', request.failure().errorText, request.url());
              if (request.resourceType() == 'media') {
                  console.log('[requestfailed] Ignoring failed media request for %s', request.url());
              } else if (ignore404Exact.includes(request.url().split('/')[-1]) || ignore404Contains.some(v => request.url().includes(v))) {
                  console.log('[requestfailed] Ignoring request for %s', request.url());
              } else if (response.url().toLowerCase().endsWith("pdf")) {
                  console.log('[requestfailed] Ignoring failed request for PDF file at %s', request.url());
              } else {
                  process.exit(124);
              }
            });

        checkURL = baseURL + localFile;
        console.log('-> Opening file %s', checkURL);
        const open = await page.goto(checkURL, { waitUntil: 'networkidle0', timeout: 0 });

        if ('click' in tests[i]) {
            for (j in tests[i]['click']) {
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
        await page.waitForTimeout(5000);
        //await page.waitForNavigation();
    }
    await browser.close();
    await server.close();
})();
