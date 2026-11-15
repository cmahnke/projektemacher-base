/*
 * Theme-owned replacement for the `iiif-kasane/element` entry point.
 *
 * The package's <iiif-viewer> element builds its React props from a fixed
 * whitelist (tab, panelOpen, pager, environment) and has no way to pass
 * `hidePanels` to the underlying Viewer. To hide the viewer's own 'puzzle'
 * and 'inference' side panel tabs by default, this module defines the same
 * element (same attributes, options parsing, locale/theme fallback and
 * runtime stylesheet injection) and adds the hard-coded
 * `hidePanels: ['puzzle', 'inference']`.
 *
 * When upstream adds hidePanels support to the element, this file can go
 * back to the plain `import "iiif-kasane/element"`.
 */

import { createElement } from 'react';
import { createRoot } from 'react-dom/client';
import { Viewer, type InfoTab } from 'iiif-kasane';
import { decodeContentState } from 'iiif-kasane/core';
// Side-effect import: registers the 3D scene display. The upstream element
// bundle includes it statically, the React library entry does not.
import 'iiif-kasane/scene';

/*
 * Tabs the element accepts via the 'options' attribute. The InfoTab type
 * allows arbitrary ids, but the element only whitelists these two.
 */
const TABS: readonly InfoTab[] = ['metadata', 'annotations'];

/*
 * The viewer's own side panel tabs that are hidden by default. The package
 * exposes them as host-page feature tabs (see the iiif-kasane README);
 * this theme does not host them, so they are dropped.
 */
const HIDDEN_PANELS: readonly string[] = ['puzzle', 'inference'];

interface ViewerOptions {
  tab?: InfoTab;
  panelOpen?: boolean;
  pager?: boolean;
  environment?: string;
}

function parseOptions(raw: string | null): ViewerOptions {
  if (!raw) return {};
  try {
    const json: unknown = JSON.parse(raw);
    if (typeof json !== 'object' || json === null) return {};
    const { tab, panelOpen, pager, environment } = json as {
      tab?: unknown;
      panelOpen?: unknown;
      pager?: unknown;
      environment?: unknown;
    };
    return {
      ...(typeof tab === 'string' && (TABS as readonly string[]).includes(tab)
        ? { tab: tab as InfoTab }
        : {}),
      ...(typeof panelOpen === 'boolean' ? { panelOpen } : {}),
      ...(typeof pager === 'boolean' ? { pager } : {}),
      ...(typeof environment === 'string' ? { environment } : {}),
    };
  } catch {
    return {};
  }
}

/*
 * The upstream element injects its stylesheet at runtime via
 * `new URL('style.css', import.meta.url)` relative to the bundle URL, so
 * the bundle must be built as ESM and the package stylesheet has to be
 * published as a sibling of the bundle ('ts/iiif/style.css', mounted from
 * the package by the theme's module mounts).
 */
function ensureStyle(): void {
  if (typeof document === 'undefined' || document.querySelector('link[data-iiif-viewer-style]')) {
    return;
  }
  const link = document.createElement('link');
  link.rel = 'stylesheet';
  link.href = new URL('style.css', import.meta.url).href;
  link.setAttribute('data-iiif-viewer-style', '');
  document.head.appendChild(link);
}

class IiifViewerElement extends HTMLElement {
  private root: ReturnType<typeof createRoot> | null;
  private container: HTMLElement | null;
  private tab?: InfoTab;

  constructor() {
    super();
    this.root = null;
    this.container = null;
  }

  static get observedAttributes(): string[] {
    return ['iiif-content', 'locale', 'theme', 'options'];
  }

  connectedCallback(): void {
    if (!this.container) {
      this.container = document.createElement('div');
      this.container.className = 'iiif-viewer-host';
      this.appendChild(this.container);
    }
    this.tab ??= parseOptions(this.getAttribute('options')).tab;
    this.root ??= createRoot(this.container);
    this.render();
  }

  disconnectedCallback(): void {
    this.root?.unmount();
    this.root = null;
  }

  attributeChangedCallback(name: string): void {
    if (name === 'options') {
      this.tab = parseOptions(this.getAttribute('options')).tab;
    }
    if (this.root) this.render();
  }

  private render(): void {
    if (!this.root) return;
    const content = decodeContentState(this.getAttribute('iiif-content'));
    if (!content) {
      this.root.render(
        createElement(
          'div',
          {
            role: 'alert',
            style: { padding: '1rem', fontSize: '0.875rem' },
          },
          'iiif-content is missing or not a manifest URL / content state.',
        ),
      );
      return;
    }
    const locale = (this.getAttribute('locale') ?? document.documentElement.lang)
      .toLowerCase()
      .startsWith('en')
      ? 'en'
      : 'ja';
    const themeAttr = this.getAttribute('theme');
    const theme = themeAttr === 'light' || themeAttr === 'dark' || themeAttr === 'auto'
      ? themeAttr
      : 'auto';
    const options = parseOptions(this.getAttribute('options'));
    this.root.render(
      createElement(Viewer, {
        iiifContent: content,
        locale,
        theme,
        tab: this.tab,
        panelOpen: options.panelOpen,
        pager: options.pager,
        environment: options.environment,
        hidePanels: HIDDEN_PANELS,
        onTabChange: (next: InfoTab) => {
          this.tab = next;
          this.render();
        },
        className: 'h-full',
      }),
    );
  }
}

ensureStyle();
if (typeof customElements !== 'undefined') {
  if (!customElements.get('iiif-kasane')) {
    customElements.define('iiif-kasane', IiifViewerElement);
  }
  if (!customElements.get('iiif-viewer')) {
    customElements.define('iiif-viewer', class extends IiifViewerElement {});
  }
}
