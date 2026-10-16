/*
 * Ambient declarations for packages that don't ship TypeScript types.
 * This must stay a script file (no imports/exports on the top level) —
 * otherwise the declarations would become module augmentations, which
 * require the augmented module to be typed already.
 */

declare module 'pdfobject' {
  interface PDFObjectOptions {
    [key: string]: unknown;
  }
  interface PDFObjectAPI {
    embed(url: string, target: string | HTMLElement, options?: PDFObjectOptions): unknown;
  }
  const PDFObject: PDFObjectAPI;
  export default PDFObject;
}

declare module 'tify' {
  interface TifyOptions {
    container?: string | HTMLElement;
    manifestUrl?: string;
    language?: string;
    translationsDirUrl?: string;
    [key: string]: unknown;
  }
  const Tify: new (options?: TifyOptions) => unknown;
  export default Tify;
}
