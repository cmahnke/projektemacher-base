import { CuttingTable } from '@projektemacher/lucienne';

function lucienne(
  element: string | HTMLElement,
  urlInput: boolean,
  resize: boolean,
  download: boolean,
  autoLoad: boolean,
  urls: string | object,
  shifts: boolean,
): unknown {
  let obj: URL | object | string;
  if (typeof urls === 'object') {
    obj = urls;
  } else {
    try {
      obj = JSON.parse(urls);
    } catch {
      try {
        obj = new URL(urls);
      } catch {
        obj = new URL(new URL(window.location.href).origin + urls);
      }
    }
  }

  return new CuttingTable(
    element as HTMLDivElement,
    urlInput,
    resize,
    download,
    autoLoad,
    obj as URL,
    shifts,
  );
}

window.lucienne = lucienne;
