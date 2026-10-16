import Tify from 'tify';

function addTify(selector: string, uri: string, lang: string = 'en'): unknown {
  if (document.documentElement.lang !== undefined) {
    lang = document.documentElement.lang;
  }

  const tify = new Tify({
    container: selector,
    manifestUrl: uri,
    language: lang,
    translationsDirUrl: '/tify/translations/',
  });
  return tify;
}

window.iiifPresentationViewer = addTify;
