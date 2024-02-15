const { detect } = require('detect-browser');
const detected = detect();

function browserBanner(banner, browsers) {
  if (detected && browsers.includes(detected.name)) {
    banner.style.display = 'block';
  }
  console.log(detected, browsers);
}

window.browserBanner = browserBanner;
