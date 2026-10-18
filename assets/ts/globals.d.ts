/*
 * Type declarations for the global APIs the theme's script entry points
 * attach to `window`.
 */

declare global {
  interface Window {
    audioplayer(elem: HTMLElement, src: string, btn: HTMLButtonElement): void;
    browserBanner(banner: HTMLElement, browsers: string[], parent: HTMLElement): void;
    browserDisableSelector(selector: string, browsers: string[]): void;
    addCopyToClipboard(button: HTMLButtonElement, content: HTMLTextAreaElement): void;
    addFSToggle(button: HTMLButtonElement, elem: HTMLElement): void;
    addPDFViewer(elemId: string, url: string, options?: object): unknown;
    addConsent(
      toggle: HTMLInputElement,
      overlay: HTMLElement,
      cookie: string,
      iframe: string,
    ): void;
    addMap(
      element: string | HTMLElement,
      url: string,
      rotation?: number,
      baseURL?: string,
      hdr?: boolean,
    ): unknown;
    initMap(
      element: string,
      url: string,
      source?: string,
      cluster?: boolean,
      marker?: string | boolean | object,
    ): unknown;
    animatedMap(
      element: string | HTMLElement,
      url: string,
      rotation?: number,
      baseURL?: string,
      initialZoom?: number,
      animation?: object | object[],
      moElement?: HTMLElement,
      initialCenter?: number[],
    ): unknown;
    iiifPresentationViewer(selector: string, uri: string): unknown;
    lucienne(
      element: string | HTMLElement,
      urlInput: boolean,
      resize: boolean,
      download: boolean,
      autoLoad: boolean,
      urls: string | object,
      shifts: boolean,
    ): unknown;
    mermaid: unknown;
    PDFObject: unknown;
  }
}

export {};
