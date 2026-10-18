/*
 * Ambient declarations for packages that don't ship TypeScript types.
 * This must stay a script file (no imports/exports on the top level) —
 * otherwise the declarations would become module augmentations, which
 * require the augmented module to be typed already.
 */

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

declare module '@pagefind/modular-ui' {
  export interface PagefindFilterValues {
    [key: string]: number;
  }
  export interface PagefindFilters {
    available?: Record<string, PagefindFilterValues>;
    selected?: Record<string, PagefindFilterValues>;
    [key: string]: unknown;
  }
  export class Instance {
    constructor(options?: { bundlePath?: string });
    add(component: Input | ResultList | FilterPills): void;
    on(event: 'filters', listener: (data: PagefindFilters) => void): void;
    triggerSearch(query: string): void;
    triggerLoad(): void;
  }
  export class Input {
    constructor(options: { inputElement: string });
  }
  export class ResultList {
    constructor(options: { containerElement: string });
  }
  export class FilterPills {
    total?: boolean;
    constructor(options: {
      containerElement: string;
      filter: string;
      selectMultiple?: boolean;
      alwaysShow?: boolean;
    });
    pillInner(val: string, count: number): string;
  }
}
