import { Instance, Input, ResultList, FilterPills } from "@pagefind/modular-ui";
import i18next from "i18next";
import LanguageDetector from "i18next-browser-languagedetector";

/*
 * Display names for the values of the section (blog) filter. These are
 * proper names and are used for every language. Keys with dots (e.g.
 * 'labs.projektemacher') require keySeparator: false in the i18next setup.
 */
const sectionLabels: Record<string, string> = {
  "backsteinexpressionismus": "Backsteinexpressionismus",
  "blaufusstoelpel": "Blaufußtölpel",
  "briefsteller": "Briefsteller",
  "christianmahnke": "Christian Mahnke",
  "diapraesentation": "Diapräsentation",
  "flohmarktfunde": "Flohmarktfunde",
  "haesslicheplastiktiereundzeugs": "Hässliche Plastiktiere und Zeugs",
  "kinderbuecher": "Kinderbücher",
  "kleiderbuegel": "Kleiderbügel",
  "kraehenbeisser": "Krähenbeißer",
  "labs.projektemacher": "Projektemacher Labs",
  "merch.projektemacher": "Projektemacher Merch",
  "never-built": "Never Built Göttingen",
  "plastikwarenfabrik": "Klaus-Ingo's Plastikwarenfabrik",
  "ric-unknownartist": "Ric – An unknown artist",
  "schriftmuster": "Schriftmuster",
  "vintagereality": "Vintage Reality",
  "vorsatzpapier": "Vorsatzpapier",
  "yaapb": "Yet another analog photo blog"
};

const translations: Record<string, Record<string, Record<string, string>>> = {
  "en": {
    "search-filter": {
      "section": "Section",
      "tag": "Tag",
      "type": "Entity type",
      "blog": "Blog",
      "all": "Alle"
    },
    "search-sections": {
      "collections": "Collections",
      "home": "Homepage",
      "iiif": "IIIF",
      "links": "Links",
      "post": "Blog",
      "All": "All",
      ...sectionLabels
    }
  },
  "de": {
    "search-filter": {
      "section": "Bereich",
      "tag": "Schlagwort",
      "type": "Entitätstyp",
      "blog": "Blog",
      "all": "Alle"
    },
    "search-sections": {
      "collections": "Sammlungen",
      "home": "Startseite",
      "iiif": "IIIF",
      "links": "Links",
      "post": "Blog",
      "All": "Alle",
      ...sectionLabels
    }
  }
}

class CMFilterPills extends FilterPills {
  pillInner(val: string, count: number): string {
    let label = val
    if (i18next.exists(`search-sections:${val}`)) {
      label = i18next.t(`search-sections:${val}`)
    }
    if (this.total) {
        return `<span aria-label="${label}" data-filter-count="${count}">${label} (${count})</span>`;
    } else {
        return `<span aria-label="${label}">${label}</span>`;
    }
  }

  /*
   * Replaces the vendored FilterPills registration:
   * - Counts always come from the query scoped totals (filters.total), so
   *   selecting a pill doesn't zero out the other pills of the same filter
   *   group — within one group a page can only match a single value, which
   *   makes drill down counts useless there.
   * - Values without hits are dropped (except 'All').
   * - Pills are sorted by hit count, descending.
   * - The pills are shown as soon as the index metadata is loaded, without
   *   waiting for the first search.
   */
  register(instance: Instance): void {
    this.instance = instance;
    instance.on("filters", (filters) => {
      if (!this.pillContainer) return;

      const values = (filters.total ?? {})[this.filter];
      if (!values) {
        console.warn(`[Pagefind FilterPills component]: No possible values found for the ${this.filter} filter`);
        this.wrapper?.setAttribute("data-pfmod-hidden", "true");
        return;
      }

      const available = Object.entries(values)
        .filter(([, count]) => count > 0)
        .sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]));

      this.available = available;
      if (!available.length) {
        this.wrapper?.setAttribute("data-pfmod-hidden", "true");
        return;
      }
      /* 'All' carries the unfiltered result count; before the first search
         no results event has fired, so fall back to the sum of the values. */
      const allCount = this.total || available.reduce((sum, [, count]) => sum + count, 0);
      this.available.unshift(["All", allCount]);
      this.wrapper?.removeAttribute("data-pfmod-hidden");
      this.update();
    });

    instance.on("results", (results) => {
      if (!this.pillContainer) return;
      this.total = results?.unfilteredResultCount || 0;

      if (this.available?.[0]?.[0] === "All") {
        this.available[0][1] = this.total;
      }

      if (this.total || this.alwaysShow) {
        this.wrapper?.removeAttribute("data-pfmod-hidden");
      } else {
        this.wrapper?.setAttribute("data-pfmod-hidden", "true");
      }
      this.update();
    });
  }
}

i18next.use(LanguageDetector).init({
  debug: false,
  fallbackLng: "de",
  resources: translations,
  supportedLngs: ['de', 'en'],
  /* Filter values contain dots ('labs.projektemacher'), so key splitting
     must be disabled to resolve them. */
  keySeparator: false,
});

window.addEventListener('DOMContentLoaded', () => {
  /* Path of the pagefind index bundle, relative or absolute. Set per page
     ('searchBundlePath' front matter) or site wide (same key in site params)
     via the emitted 'data-bundle-path' attribute — defaults to '/index/',
     which only works for deployments at a domain root. */
  const bundlePath =
      document.querySelector(".searchbox")?.getAttribute("data-bundle-path") ?? "/index/"
  const urlParams = new URLSearchParams(window.location.search);
  const query = urlParams.get('q');
  const searchInputSelector = "#search-box";
  const searchInput = document.querySelector<HTMLInputElement>(searchInputSelector)!;
  const filterContainer = document.querySelector("#search-filter")!;
  let filterInitialized = false

  searchInput.addEventListener("input", (event: Event) => {
    const newQuery = (event.target as HTMLInputElement).value
    urlParams.set("q", newQuery);
    history.replaceState(null, "", "?"+urlParams.toString());
  })

  document.querySelector('.search-button')!.addEventListener("click", () => {
    const enterEvent = new KeyboardEvent('keydown', {
      key: 'Enter',
      code: 'Enter',
      which: 13,
      keyCode: 13,
    });
    searchInput.dispatchEvent(enterEvent);
  })

  const instance = new Instance({
      bundlePath: bundlePath,
      /* Pagefind runs the index in a web worker; worker requests bypass the
         request interception used by the QA checks, so keep the index loading
         on the main thread when driven by automation (navigator.webdriver) */
      noWorker: navigator.webdriver === true
  });
  instance.add(new Input({
      inputElement: searchInputSelector
  }));
  instance.on("filters", (filters) => {
    if (!filterInitialized) {
      for (const [filter, _values] of Object.entries(filters.available ?? {})) {
        let filterLabel = filter
        if (i18next.exists(`search-filter:${filter}`)) {
          filterLabel = i18next.t(`search-filter:${filter}`)
        }
        const filterElementId = `search-filter-${filter}`
        const filterElement = document.createElement("fieldset");
        const filterElementLabel = document.createElement("legend");
        filterElementLabel.innerText = filterLabel

        filterElement.id = filterElementId
        filterElement.classList.add(filter)
        filterElement.classList.add("search-filter-single")
        filterContainer.appendChild(filterElement)
        instance.add(new CMFilterPills({
          containerElement: `#${filterElementId}`,
          filter: filter,
          selectMultiple: true,
          alwaysShow: false
        }));
        filterElement.appendChild(filterElementLabel)
      }
      filterInitialized = true
    }
  });

  instance.add(new ResultList({
      containerElement: "#search-results"
  }));


  searchInput.focus();
  if (query !== null && query !== "") {
    searchInput.value = query;
    instance.triggerSearch(query)
  } else {
      instance.triggerLoad();
  }

})
