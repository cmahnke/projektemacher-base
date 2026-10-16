import { detect } from 'detect-browser';

const detected = detect();

export function browserBanner(banner: HTMLElement, browsers: string[], parent: HTMLElement): void {
  parent.insertBefore(banner, parent.firstChild);
  if (detected && browsers.includes(detected.name)) {
    banner.style.display = 'block';
  }
  console.log(detected, browsers);
}

export function browserDisableSelector(selector: string, browsers: string[]): void {
  document.addEventListener('DOMContentLoaded', () => {
    if (detected && browsers.includes(detected.name)) {
      const selected = document.querySelectorAll(selector);
      selected.forEach((elem) => {
        (elem as HTMLElement).style.display = 'none';
      });
    }
  });
}

window.browserBanner = browserBanner;
window.browserDisableSelector = browserDisableSelector;
