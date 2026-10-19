/*
 * Ambient declarations for packages that don't ship TypeScript types.
 * This must stay a script file (no imports/exports on the top level) —
 * otherwise the declarations would become module augmentations, which
 * require the augmented module to be typed already.
 */

/*
 * `@projektemacher/hdr-canvas` declares `HDRHTMLCanvasElement` but doesn't
 * export it — mirror its shape globally so the type stays usable.
 */
interface HDRHTMLCanvasElement extends HTMLCanvasElement {
  configureHighDynamicRange(options: { mode?: string }): void;
  _getContext(contextId: string, options?: object): RenderingContext | null;
}

declare module '@projektemacher/hdr-canvas/three/WebGPU.js' {
  const WebGPU: {
    isAvailable(): boolean;
  };
  export default WebGPU;
}

declare module '@projektemacher/hdr-canvas/three/HDRWebGPURenderer.js' {
  export class HDRWebGPURenderer {
    domElement: HTMLCanvasElement;
    constructor(options?: { canvas?: HTMLCanvasElement; antialias?: boolean });
    setPixelRatio(value: number): void;
    setSize(width: number, height: number): void;
    setAnimationLoop(callback: () => void): void;
    setClearColor(color: number, alpha?: number): void;
    render(scene: unknown, camera: unknown): void;
  }
  export default HDRWebGPURenderer;
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

/*
 * `aframe` ships no TypeScript types; the namespace (with a `default`
 * export) is exposed as a global by the module build itself.
 * `aframe-orbit-controls` is a plain script without exports that
 * registers on the global `AFRAME` object.
 */
declare module 'aframe' {
  const AFRAME: Record<string, unknown> & { default?: unknown };
  export default AFRAME;
}

declare module 'aframe-orbit-controls';

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
