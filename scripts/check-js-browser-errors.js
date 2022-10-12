const puppeteer = require ('puppeteer')
const fs = require('fs');
const path = require('path');
const express = require('express');

const urlsFile = 'test-urls.txt';
const contentDir = 'docs'
const localFilePrefix = 'file:./';

if (!fs.existsSync(contentDir)) {
    console.log('Directory %s doesn\'t exist!', contentDir);
    process.exit(1);
}

var urls
if (fs.existsSync(urlsFile)) {
    urls = fs.readFileSync(urlsFile).toString().split("\n");
} else {
  console.log('File %s not found!', urlsFile);
  urls = ['/'];
}

(async () => {
    const browser = await puppeteer.launch ({
        headless: true,
        devtools: false,
        ignoreHTTPSErrors: true
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
            });

        console.log('Opening file %s', localFile);
        const open = await page.goto(localFilePrefix + localFile, { waitUntil: 'networkidle2', timeout: 0 });


    }
    await browser.close();
})();
