const puppeteer = require ('puppeteer')
const fs = require('fs');
const path = require('path');
const toml = require('toml');
const yargs = require('yargs');
const express = require('express');
const cors = require('cors');
const app = express();

/* Settings */
const urlsFile = 'test-urls.txt';
const configFile = 'config.toml';
const contentDir = 'docs'
const localFilePrefix = 'file:./';
const localPort = 3000;
const ignore404 = ['favicon.ico'];

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

var urls
if (fs.existsSync(urlsFile)) {
    urls = fs.readFileSync(urlsFile).toString().split("\n");
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

(async () => {

    app.use(cors());
    const webRoot = path.join(process.cwd(), contentDir, '/');
    app.use(express.static(webRoot));
    var server = app.listen(localPort, function () {
        console.log('Webserver started, serving \'%s\'', webRoot);
    });

    const browser = await puppeteer.launch ({
        /*userDataDir: path.resolve(__dirname, './puppeteerTmp'),*/
        headless: true,
        devtools: false,
        args:['--use-gl=egl']
         /* '--disable-web-security', '--allow-failed-policy-fetch-for-test', '--allow-running-insecure-content', '--unsafely-treat-insecure-origin-as-secure=' + baseURL] */
    })
    const page = await browser.newPage();
    await page.setRequestInterception(true);

    page.on('request', request => {
        const headers = request.headers();
        var newRequestUrl;
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
            console.log('Got response for %s', response.url())
        });

    for (var i in urls) {
        var localFile;
        if (urls[i] == '/') {
            localFile = 'index.html';
        } else {
            localFile = urls[i];
        }
        localFile = localFile.replace(baseURL, '/')
        if (urls[i].startsWith('/')) {
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

        page.on('console', msg => console.log('Browser console:', msg.text()))
            .on('pageerror', error => {
              console.log(error.message);
              process.exit(123);
            })
            .on('requestfailed', request => {
              console.log('Got error \'%s\' for \'%s\'', request.failure().errorText, request.url());
              if (request.resourceType() == 'media') {
                  console.log('Ignoring failed media request for %s', request.url());
              } else if (ignore404.includes(request.url().split('/')[-1])) {
                  console.log('Ignoring request for %s', request.url());
              } else {
                  process.exit(124);
              }
            });

        checkURL = baseURL + localFile;
        console.log('Opening file %s', checkURL);
        const open = await page.goto(checkURL, { waitUntil: 'networkidle2', timeout: 0 });

    }
    await browser.close();
    await server.close();
})();
