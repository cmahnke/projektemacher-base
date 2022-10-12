const puppeteer = require ('puppeteer')
const fs = require('fs');
const urlsFile = 'test-urls.txt';
const localFilePrefix = 'file:./content/';

/*TODO: Load Urls  */
var urls
if (fs.existsSync(urlsFile )) {
    urls = fs.readFileSync(urlsFile).toString().split("\n");
} else {
  console.log(' File %s not found!', urlsfile);
  urls = ['/'];
}

(async () => {
    const browser = await puppeteer.launch ({
        headless: true,
        devtools: false
    })

    for (var url in urls) {
        if (url == '/') {
          url = 'index.html';
        }

        const open = await page.goto ( localFilePrefix + url, { waitUntil: 'networkidle2', timeout: 0 });

        const html = await page.content();

    }
})
