const puppeteer = require ('puppeteer')
const fs = require('fs');
const urlsFile = 'test-urls.txt';
const contentDir = 'docs'
const localFilePrefix = 'file:./' + contentDir + '/';

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
        devtools: false
    })
    const page = await browser.newPage();

    for (var i in urls) {
        var localFile;
        if (urls[i] == '/') {
          localFile = localFilePrefix + 'index.html';
        } else {
          localFile = localFilePrefix + urls[i];
        }

        if (!fs.existsSync(localFile)) {
            console.log('Local file %s doesn\'t exist, skipping!', localFile);
            continue;
        }


        console.log('Opening file %s', localFile);
        const open = await page.goto(localFile, { waitUntil: 'networkidle2', timeout: 0 });

        const html = await page.content();

    }
    await browser.close();
})();
