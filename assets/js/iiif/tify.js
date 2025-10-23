import 'tify';

function addTify (selector, uri, lang = 'en') {
  if (document.documentElement.lang !== undefined) {
    lang = document.documentElement.lang;
  }

  const tify = new Tify({
    container: selector,
    manifestUrl: uri,
    language: lang,
    translationsDirUrl: '/tify/translations/'
  });
  return tify;
}

window.iiifPresentationViewer = addTify;
