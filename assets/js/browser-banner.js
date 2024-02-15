const { detect } = require('detect-browser');
const detected = detect();

function browserBanner(banner, browsers) {
  if (detected && browsers.includes(detected.name)) {
    banner.style.display = 'block';
  }
  console.log(detected, browsers);
}

function browserDisableSelector(selector, browsers) {
  document.addEventListener("DOMContentLoaded", function() {
    if (detected && browsers.includes(detected.name)) {
      const selected = document.querySelectorAll(selector);
      selected.forEach((elem) => {
        elem.style.display = 'none';
      });
    }
  });

}

window.browserBanner = browserBanner;
window.browserDisableSelector = browserDisableSelector;
