const puppeteer = require ('puppeteer')
const fs = require('fs');
const path = require('path');
const express = require('express');
const cors = require('cors');
const toml = require('toml');
const app = express();

const urlsFile = 'test-urls.txt';
const configFile = 'config.toml';
const contentDir = 'docs'
const localFilePrefix = 'file:./';
const localPort = 3000;

if (!fs.existsSync(contentDir)) {
    console.log('Directory %s doesn\'t exist!', contentDir);
    process.exit(1);
}

if (!fs.existsSync(configFile)) {
    console.log('Hugo configuration %s doesn\'t exist in current directory (%s), are you sure, it\'s containig a Hugo site?', configFile, process.cwd());
    process.exit(2);
}

var urls
if (fs.existsSync(urlsFile)) {
    urls = fs.readFileSync(urlsFile).toString().split("\n");
} else {
  console.log('File %s not found!', urlsFile);
  urls = ['/'];
}

const hugoConfig = toml.parse(fs.readFileSync(configFile).toString());
var baseURL = hugoConfig.baseURL;
const remotePrefix = 'http://localhost:' + localPort + '/';
if (baseURL == '') {
    baseURL = 'http://localhost:' + localPort + '/';
}
console.log('Base URL is %s', baseURL);

(async () => {

    app.use(cors());
    app.use(express.static(path.join(__dirname, contentDir)));
    var server = app.listen(localPort, function () {
        console.log('Webserver started');
    });

    const browser = await puppeteer.launch ({
        headless: true,
        devtools: false,
        args: ['--disable-web-security']
        /* , ignoreHTTPSErrors: true */
    })
    const page = await browser.newPage();
    await page.setRequestInterception(true);

    page.on('request', request => {
        var newRequestUrl
        if (request.url().startsWith(baseURL)) {
            newRequestUrl = request.url().replace(baseURL, remotePrefix)
            console.log("Mapping request for '%s' to '%s'", request.url(), newRequestUrl);
            request.continue({
                url: newRequestUrl
            });
            return;
        }
        request.continue();
        })
        .on('response', response => {
            console.log('Got response for %s', response.url())
        });

    for (var i in urls) {
        var localFile;
        if (urls[i] == '/') {
          localFile = 'index.html';
        } else {
          localFile = urls[i];
        }

        if (!fs.existsSync(path.join(process.cwd(),  contentDir, localFile))) {
            console.log('Local file %s doesn\'t exist, skipping!', localFile);
            continue;
        }

        page.on('console', msg => console.log('Browser console:', msg.text()))
            .on('pageerror', error => {
              console.log(error.message);
              process.exit(123);
            })
            .on('requestfailed', request => {
              console.log(`${request.failure().errorText} ${request.url()}`);
              process.exit(124);
            });

        checkURL = baseURL + localFile;
        console.log('Opening file %s', checkURL);
        const open = await page.goto(checkURL, { waitUntil: 'networkidle2', timeout: 0 });

    }
    await browser.close();
    await server.close();
})();
