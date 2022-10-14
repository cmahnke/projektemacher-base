const puppeteer = require ('puppeteer')
const fs = require('fs');
const path = require('path');
const express = require('express');
const cors = require('cors');
const url = require('url');
const proxy = require('express-http-proxy');
const toml = require('toml');
const app = express();

const urlsFile = 'test-urls.txt';
const configFile = 'config.toml';
const contentDir = 'docs'
const localFilePrefix = 'file:./';
const localPort = 3000;
const remotePrefix = 'http://localhost:' + localPort;

if (!fs.existsSync(contentDir)) {
    console.log('Directory %s doesn\'t exist!', contentDir);
    process.exit(1);
}

if (!fs.existsSync(configFile)) {
    console.log('Hugo configuration %s doesn\'t exist in current directory (%s), are you sure, it\'s containig a Hugo site?', configFile, process.cwd());
    process.exit(1);
}

var urls
if (fs.existsSync(urlsFile)) {
    urls = fs.readFileSync(urlsFile).toString().split("\n");
} else {
  console.log('File %s not found!', urlsFile);
  urls = ['/'];
}

const hugoConfig = toml.parse(fs.readFileSync(configFile).toString());
const baseURL = hugoConfig.baseURL;
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
        args: [ '--proxy-server=127.0.0.1:${localPort}' ]
        /* , ignoreHTTPSErrors: true */
    })
    const page = await browser.newPage();

    for (var i in urls) {
        var localFile;
        if (urls[i] == '/') {
          localFile = path.join(process.cwd(),  contentDir, 'index.html');
        } else {
          localFile = path.join(process.cwd(),  contentDir, urls[i]);
        }

        if (!fs.existsSync(localFile)) {
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

        console.log('Opening file %s', localFile);
        const open = await page.goto(localFilePrefix + localFile, { waitUntil: 'networkidle2', timeout: 0 });


    }
    await browser.close();
    await server.close();
})();
