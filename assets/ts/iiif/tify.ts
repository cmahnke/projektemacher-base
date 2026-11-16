import Tify from 'tify';
import { navPlacePlugin } from '@projektemacher/tify-plugin-navplace';

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
  navPlacePlugin(tify, {}).catch((err) => console.error('navPlace plugin failed:', err));
  return tify;
}

window.iiifPresentationViewer = addTify;
