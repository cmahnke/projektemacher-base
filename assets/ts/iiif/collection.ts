import '@mango-iiif/collection-navigator';
import { collectionSelectEvent, type CollectionSelection } from '@mango-iiif/collection-navigator';
import { bindCollectionToMango } from '@mango-iiif/collection-navigator/mango';
import { Mango } from '@mango-iiif/iiif-viewer';
import type {
  CollectionTreeMessages,
  IIIFStructure,
  MangoCollectionTreeElement,
  StructureNode,
} from '@mango-iiif/collection-navigator';

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

  let viewer: Mango | null = null;

  const mount = (manifestId: string): Mango => {
    if (viewer === null) {
      container.innerHTML = '';
      viewer = new Mango({
        target: container as HTMLElement,
        manifestId,
        config: {
          language: lang,
          showCollection: false,
        },
      });
      bindCollectionToMango(tree, viewer);
    }
    return viewer;
  };

  const navigate = (selection: CollectionSelection): void => {
    if (!selection.manifestId) {
      return;
    }
    const active = mount(selection.manifestId);
    if (active.getManifestId() !== selection.manifestId) {
      active.setManifest(selection.manifestId);
    }
  };

  tree.addEventListener(collectionSelectEvent, ((event: CustomEvent<CollectionSelection>) => {
    navigate(event.detail);
  }) as EventListener);

  const empty = lang === 'de' ? 'Keine Manifeste in dieser Sammlung.' : 'No manifests in this collection.';
  const failed = lang === 'de' ? 'Die Sammlung konnte nicht geladen werden.' : 'The collection could not be loaded.';

  const message = (text: string): void => {
    container.innerHTML = `<p class="collection-browser-message">${text}</p>`;
  };

  void tree
    .load(uri)
    .then((structure) => {
      const first = findFirstManifestId(structure);
      if (first === null) {
        message(empty);
        return;
      }
      navigate({ node: structure.root, manifestId: first });
    })
    .catch(() => {
      message(failed);
    });

  return {
    tree,
    get viewer(): Mango | null {
      return viewer;
    },
  };
}

window.iiifCollectionBrowser = iiifCollectionBrowser;
