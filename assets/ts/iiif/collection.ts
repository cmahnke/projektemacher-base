import Tify from 'tify';
import '@mango-iiif/collection-navigator';
import type {
  CollectionSelection,
  CollectionTreeMessages,
  IIIFStructure,
  MangoCollectionTreeElement,
  StructureNode,
} from '@mango-iiif/collection-navigator';

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

const germanMessages: Partial<CollectionTreeMessages> = {
  viewBy: 'Ansicht',
  hierarchy: 'Hierarchie',
  date: 'Datum',
  loadingDateMetadata: 'Metadaten für Datumsangaben werden geladen …',
  loadNextDates: 'Weitere laden',
  loadMissingDate: 'Fehlendes laden',
  loadMissingDates: 'Fehlende laden',
  dateNotLoaded: 'Datum nicht geladen',
  oneDateNotLoaded: 'Datum nicht geladen',
  datesNotLoaded: 'Daten nicht geladen',
  undated: 'Undatiert',
  expand: 'Ausklappen',
  collapse: 'Einklappen',
  retry: 'Erneut versuchen',
  loadingStructure: 'Struktur wird geladen …',
  noResource: 'Keine Ressource geladen',
  noNavigableItems: 'Keine navigierbaren Einträge vorhanden',
  navigationLabel: 'Sammlungsnavigation',
};

interface TifyInstance {
  destroy(): void;
}

function findFirstManifestId(structure: IIIFStructure): string | null {
  const queue: StructureNode[] = structure.root?.children ? [...structure.root.children] : [];
  let guard = 0;
  while (queue.length > 0 && guard < 500) {
    guard++;
    const node = queue.shift() as StructureNode;
    if (node.type === 'manifest' && node.id) {
      return node.id;
    }
    if (node.children?.length > 0) {
      queue.push(...node.children);
    }
  }
  return null;
}

function iiifCollectionBrowser(treeSelector: string, viewerSelector: string, uri: string): unknown {
  const tree = document.querySelector(treeSelector) as MangoCollectionTreeElement | null;
  const container = document.querySelector(viewerSelector);
  if (tree === null || container === null) {
    return null;
  }

  const lang = (document.documentElement.lang || 'en').split('-')[0];

  if (lang === 'de') {
    tree.locale = lang;
    tree.messages = germanMessages;
  }

  let tify: TifyInstance | null = null;

  const show = (manifestId: string): void => {
    if (tify !== null) {
      tify.destroy();
      tify = null;
    }
    container.innerHTML = '';
    tify = addTify(viewerSelector, manifestId, lang) as TifyInstance;
  };

  tree.addEventListener(
    'iiif-collection-select',
    ((event: CustomEvent<CollectionSelection>) => {
      const { manifestId } = event.detail;
      if (manifestId) {
        show(manifestId);
      }
    }) as EventListener,
  );

  const empty = lang === 'de' ? 'Keine Manifeste in dieser Sammlung.' : 'No manifests in this collection.';
  const failed = lang === 'de' ? 'Die Sammlung konnte nicht geladen werden.' : 'The collection could not be loaded.';

  void tree
    .load(uri)
    .then((structure) => {
      const first = findFirstManifestId(structure);
      if (first === null) {
        container.innerHTML = `<p class="collection-browser-message">${empty}</p>`;
        return;
      }
      show(first);
    })
    .catch(() => {
      container.innerHTML = `<p class="collection-browser-message">${failed}</p>`;
    });

  return {
    get tify(): TifyInstance | null {
      return tify;
    },
    tree,
  };
}

window.iiifCollectionBrowser = iiifCollectionBrowser;
