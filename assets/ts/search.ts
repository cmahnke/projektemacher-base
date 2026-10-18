import { Instance, Input, ResultList, FilterPills } from "@pagefind/modular-ui";
import i18next from "i18next";
import LanguageDetector from "i18next-browser-languagedetector";

const translations: Record<string, Record<string, Record<string, string>>> = {
  "en": {
    "search-filter": {
      "section": "Section",
      "tag": "Tag",
      "type": "Entity type",
      "all": "Alle"
    },
    "search-sections": {
      "collections": "Collections",
      "home": "Homepage",
      "iiif": "IIIF",
      "links": "Links",
      "post": "Blog",
      "All": "All"
    }
  },
  "de": {
    "search-filter": {
      "section": "Bereich",
      "tag": "Schlagwort",
      "type": "Entitätstyp",
      "all": "Alle"
    },
    "search-sections": {
      "collections": "Sammlungen",
      "home": "Startseite",
      "iiif": "IIIF",
      "links": "Links",
      "post": "Blog",
      "All": "Alle"
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
}

i18next.use(LanguageDetector).init({
  debug: false,
  fallbackLng: "de",
  resources: translations,
  supportedLngs: ['de', 'en'],
});

window.addEventListener('DOMContentLoaded', () => {
  const bundlePath = "/index/"
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
      bundlePath: bundlePath
  });
  instance.add(new Input({
      inputElement: searchInputSelector
  }));
  instance.on("filters", (filters) => {
    if (!filterInitialized) {
      for (const [filter, _values] of Object.entries(filters.available ?? {})) {
        /*
        const filterContainer = document.createElement("ul");
        for (const [value, count] of Object.entries(values)) {
          //console.log(`${value}: ${count}`);
          const tag = document.createElement("li");
          tag.innerText = `${value} (${count})`
          filterContainer.appendChild(tag);
        }
        */
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
