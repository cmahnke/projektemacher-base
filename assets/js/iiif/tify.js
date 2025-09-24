//import * as Tify from 'tify';
import 'tify';

function addTify (id, uri, lang = 'en') {
  if (document.documentElement.lang !== undefined) {
    lang = document.documentElement.lang;
  }

  if (!id.startsWith("#")) {
    id = '#' + id;
  }

  const tify = new Tify({
    container: id,
    manifestUrl: uri,
    language: lang,
    translationsDirUrl: '/tify/translations/'
  });
  return tify;
}

window.iiifPresentationViewer = addTify;
