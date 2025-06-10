import { CuttingTable } from "./lucienne-0.1.0.js";

function lucienne(element, urlInput, gridSelector, download, autoLoad, urls, shifts) {

  let obj;
  if (typeof urls === 'object') {
    obj = urls;
  } else {
    try {
      obj = JSON.parse(urls);
    } catch {
      try {
        obj = new URL(urls);
      } catch {
        obj = new URL(window.location).origin + urls;
      }
    }
  }

  return new CuttingTable(element, urlInput, gridSelector, download, autoLoad, obj, shifts);
}

window.lucienne = lucienne;
