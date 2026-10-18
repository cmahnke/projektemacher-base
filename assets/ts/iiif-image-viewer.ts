/* Inspired from https://openlayers.org/en/latest/examples/iiif.html and several others  */

import IIIF from 'ol/source/IIIF';
import IIIFInfo from 'ol/format/IIIFInfo';
import Map from 'ol/Map';
import TileLayer from 'ol/layer/Tile';
import View, { Animation, AnimationOptions, ViewOptions } from 'ol/View';
import { Control, FullScreen, Rotate, Zoom } from 'ol/control';
import { Coordinate } from 'ol/coordinate';
import { Extent } from 'ol/extent';
import { fromUserCoordinate, fromUserExtent } from 'ol/proj.js';
import { defaultGetContextHDR, checkHDR, checkHDRCanvas } from '@projektemacher/hdr-canvas';

type RunningAnimation = Animation & AnimationOptions;

interface TooltipTranslations {
  [key: string]: string;
}

interface RotateControlOptions {
  tipLabel?: string;
  target?: HTMLElement | string;
}

class AnimatedView extends View {
  pauseableAnimations_: AnimationOptions[];
  animationsPointer_: number;
  lastAnimation_: AnimationOptions;
  initalCenter: Coordinate | undefined;

  constructor(opt_options?: ViewOptions) {
    super(opt_options);

    this.pauseableAnimations_ = [];
    this.animationsPointer_ = -1;
    this.lastAnimation_ = {};
    this.initalCenter = this.getCenter() || undefined;
  }

  // Emulate a ring data structure
  getPauseableAnimation_(): AnimationOptions {
    if (this.pauseableAnimations_.length - 1 > this.animationsPointer_) {
      this.animationsPointer_++;
      return this.pauseableAnimations_[this.animationsPointer_];
    } else {
      this.animationsPointer_ = 0;
      return this.pauseableAnimations_[this.animationsPointer_];
    }
  }

  // This is the callback, when one animation has finished
  nextAnimation_(completed?: boolean): void {
    if (completed === undefined || completed) {
      const nextAnimation = this.getPauseableAnimation_();
      this.animate(nextAnimation, (state: boolean) => {
        this.nextAnimation_(state);
      });
    }
  }

  pauseAnimation(): void {
    if (!this.getAnimating()) {
      return;
    }
    // OL tracks running animations in a private field, access it directly
    const animations = (this as unknown as { animations_: (RunningAnimation[] | null)[] })
      .animations_;
    const running = animations[0];
    if (running === null || running.length === 0) {
      return;
    }
    const animation = running[0];
    //Safe state
    const now = Date.now();
    const elapsed = now - animation.start;
    const stopState: AnimationOptions = {
      center: animation.center,
      zoom: animation.zoom,
      rotation: animation.rotation,
      duration: animation.duration - elapsed,
    };
    this.lastAnimation_ = stopState;
    // Stop running animation
    this.cancelAnimations();
  }

  startAnimation_(): void {
    if (this.getAnimating()) {
      return;
    }
    // Check if we stopped, if yes, reset
    if (Object.keys(this.lastAnimation_).length !== 0) {
      this.lastAnimation_ = {};
    }
    // Get first animation,pass it to animation method and add a callback
    this.animate(this.getPauseableAnimation, (state: boolean) => {
      this.nextAnimation_(state);
    });
  }

  resumeAnimation(): void {
    if (this.getAnimating()) {
      return;
    }
    // Check if we stopped
    if (Object.keys(this.lastAnimation_).length === 0) {
      this.startAnimation_();
    } else {
      // Start stopped animation
      this.animate(this.lastAnimation_, (state: boolean) => {
        this.nextAnimation_(state);
      });
    }
  }

  setPauseableAnimation(...animations: AnimationOptions[]): void {
    this.animationsPointer_ = -1;
    this.pauseableAnimations_ = animations;
  }

  getPauseableAnimation(): AnimationOptions[] {
    return this.pauseableAnimations_;
  }

  setCenter(center: Coordinate): void {
    this.initalCenter = center;
    this.setCenterInternal(fromUserCoordinate(center, this.getProjection()));
  }

  isNoopAnimation(_animation: AnimationOptions): boolean {
    return false;
  }

  //Even though the OL API is quite good there are some beginners mistakes, like missing symetry
  setResolutions(resolutions: number[]): void {
    // OL keeps the resolutions in a private field
    (this as unknown as { resolutions_: number[] }).resolutions_ = resolutions;
  }

  setExtent(extent: Extent): void {
    const options: ViewOptions = {};
    options.extent = fromUserExtent(extent, this.getProjection()) as Extent;
    this.applyOptions_(options);
  }
}

class RotateLeftControl extends Control {
  constructor(opt_options?: RotateControlOptions) {
    const options = opt_options || {};
    const tipLabel = options.tipLabel ? options.tipLabel : 'Rotate 90° left';

    const button = document.createElement('button');
    button.innerHTML = '<i class="icon-left" aria-hidden="true"></i>';
    button.title = tipLabel;
    button.setAttribute('aria-label', tipLabel);

    const element = document.createElement('div');
    element.className = 'rotate-left ol-unselectable ol-control';
    element.appendChild(button);

    super({
      element: element,
      target: options.target,
    });

    button.addEventListener('click', this.handleRotateLeft.bind(this), false);
  }

  handleRotateLeft(): void {
    const map = this.getMap();
    if (map === null) {
      return;
    }
    const startRotation = map.getView().getRotation();
    map.getView().setRotation(startRotation + (-90 * Math.PI) / 180);
  }
}

class RotateRightControl extends Control {
  constructor(opt_options?: RotateControlOptions) {
    const options = opt_options || {};
    const tipLabel = options.tipLabel ? options.tipLabel : 'Rotate 90° right';

    const button = document.createElement('button');
    button.innerHTML = '<i class="icon-right" aria-hidden="true"></i>';
    button.title = tipLabel;
    button.setAttribute('aria-label', tipLabel);

    const element = document.createElement('div');
    element.className = 'rotate-right ol-unselectable ol-control';
    element.appendChild(button);

    super({
      element: element,
      target: options.target,
    });

    button.addEventListener('click', this.handleRotateRight.bind(this), false);
  }

  handleRotateRight(): void {
    const map = this.getMap();
    if (map === null) {
      return;
    }
    const startRotation = map.getView().getRotation();
    map.getView().setRotation(startRotation + (90 * Math.PI) / 180);
  }
}

/* TODO: Rename these functiontions if real maps are added. The following files needs to be changed aas well:
        * projektemacher-base/layouts/shortcodes/iiif/iiif.html
        * projektemacher-base/layouts/partials/iiif/iiif-image.html
        * projektemacher-base/layouts/partials/iiif/kenburns.html
 */

/*
 * The OpenLayers built-in controls name their buttons via `title`
 * only (or CSS content glyphs with no text at all) - expose the same
 * label as aria-label, so assistive technology can announce them
 * (WCAG 4.1.2).
 */
function setControlAriaLabels(map: Map, labels: [string, string][]): void {
  const root = map.getTargetElement();
  if (!root) {
    return;
  }
  labels.forEach(([selector, label]) => {
    root.querySelectorAll<HTMLElement>(selector).forEach((el) => el.setAttribute('aria-label', label));
  });
}

window.addMap = function (
  element: string | HTMLElement,
  url: string,
  rotation?: number,
  baseURL?: string,
  hdr?: boolean,
): Map {
  let initialRotation = 0;
  if (rotation !== undefined && rotation != 0) {
    initialRotation = (rotation * Math.PI) / 180;
  }
  if (hdr === undefined) {
    hdr = false;
  }
  // Languages
  let lang = 'en';
  if (document.documentElement.lang !== undefined) {
    /* See https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Intl/Locale/language */
    const locale = new Intl.Locale(document.documentElement.lang);
    lang = locale.language;
  }
  const toolTips: { [lang: string]: TooltipTranslations } = {
    de: {
      zoomIn: 'Vergrößern',
      zoomOut: 'Verkleinern',
      fullscreen: 'Vollbildansicht',
      rotate: 'Rotation zurücksetzen',
      rotateLeft: '90° nach links drehen',
      rotateRight: '90° nach rechst drehen',
    },
    en: {
      zoomIn: 'Zoom in',
      zoomOut: 'Zoom out',
      fullscreen: 'Toggle full-screen',
      rotate: 'Reset rotation',
      rotateLeft: 'Rotate 90° left',
      rotateRight: 'Rotate 90° right',
    },
  };

  console.log('Setting up ' + lang);

  if (hdr && checkHDR() && checkHDRCanvas()) {
    defaultGetContextHDR();
    console.log('Enabled HDR Canvas');
  }

  const layer = new TileLayer();
  const map = new Map({
    controls: [
      new Zoom({
        zoomInTipLabel: toolTips[lang]['zoomIn'],
        zoomOutTipLabel: toolTips[lang]['zoomOut'],
      }),
      new FullScreen({ tipLabel: toolTips[lang]['fullscreen'] }),
      new Rotate({ tipLabel: toolTips[lang]['rotate'] }),
      new RotateLeftControl({ tipLabel: toolTips[lang]['rotateLeft'] }),
      new RotateRightControl({ tipLabel: toolTips[lang]['rotateRight'] }),
    ],
    layers: [layer],
    target: element,
  });
  setControlAriaLabels(map, [
    ['.ol-zoom-in', toolTips[lang]['zoomIn']],
    ['.ol-zoom-out', toolTips[lang]['zoomOut']],
    ['.ol-full-screen button', toolTips[lang]['fullscreen']],
    ['.ol-rotate button', toolTips[lang]['rotate']],
  ]);

  fetch(url)
    .then((response) => {
      response
        .json()
        .then((imageInfo) => {
          const options = new IIIFInfo(imageInfo).getTileSourceOptions();
          if (options === undefined || options.version === undefined) {
            console.log('Data seems to be no valid IIIF image information.');
            return;
          }
          options.zDirection = -1;
          if (baseURL !== undefined && baseURL != '') {
            options.url = baseURL;
          }
          const iiifTileSource = new IIIF(options);
          layer.setSource(iiifTileSource);
          const tileGrid = iiifTileSource.getTileGrid();
          if (tileGrid === null) {
            console.log('Tile grid is missing.');
            return;
          }
          const extent = tileGrid.getExtent();
          if (extent === null) {
            console.log('Tile grid extent is missing.');
            return;
          }
          map.setView(
            new View({
              resolutions: tileGrid.getResolutions(),
              extent: extent,
              constrainOnlyCenter: true,
              rotation: initialRotation,
            }),
          );
          map.getView().fit(extent);
        })
        .catch((body) => {
          console.log('Could not read image info json. ' + body);
        });
    })
    .catch(() => {
      console.log('Could not read data from URL.');
    });
  return map;
};

/*
See https://openlayers.org/en/latest/examples/animation.html
postsaison_4_87page048.getView().animate({center:[1000,-3000], duration: 3000 zoom: view.getZoom() + 1})
postsaison_4_87page048.getView().animate({center:[1000,-3000], duration: 3000, zoom: 1})
*/

window.animatedMap = function (
  element: string | HTMLElement,
  url: string,
  rotation?: number,
  baseURL?: string,
  initialZoom?: number,
  animation?: AnimationOptions | AnimationOptions[],
  moElement?: HTMLElement,
  initialCenter?: Coordinate,
): Map {
  let initialRotation = 0;
  if (rotation !== undefined && rotation != 0) {
    initialRotation = (rotation * Math.PI) / 180;
  }

  const layer = new TileLayer();
  const map = new Map({
    controls: [],
    layers: [layer],
    target: element,
  });
  const view = new AnimatedView({
    constrainOnlyCenter: true,
    rotation: initialRotation,
  });

  fetch(url)
    .then((response) => {
      response
        .json()
        .then((imageInfo) => {
          const options = new IIIFInfo(imageInfo).getTileSourceOptions();
          if (options === undefined || options.version === undefined) {
            console.log('Data seems to be no valid IIIF image information.');
            return;
          }
          options.zDirection = -1;
          if (baseURL !== undefined && baseURL != '') {
            options.url = baseURL;
          }
          const iiifTileSource = new IIIF(options);
          layer.setSource(iiifTileSource);
          const tileGrid = iiifTileSource.getTileGrid();
          if (tileGrid === null) {
            console.log('Tile grid is missing.');
            return;
          }
          const extent = tileGrid.getExtent();
          if (extent === null) {
            console.log('Tile grid extent is missing.');
            return;
          }
          view.setExtent(extent);
          view.setResolutions(tileGrid.getResolutions());
          map.setView(view);
          map.getView().fit(extent);
          if (initialZoom !== undefined && initialZoom !== ('' as unknown as number)) {
            map.getView().setZoom(initialZoom);
          }
          if (initialCenter !== undefined && initialCenter !== ('' as unknown as Coordinate)) {
            map.getView().setCenter(initialCenter);
          }
        })
        .catch((body) => {
          console.log(`Could not read image info json from "${url}".` + body);
        });
    })
    .catch(() => {
      console.log('Could not read data from URL.');
    });

  if (animation !== undefined && animation !== ('' as unknown as AnimationOptions) && moElement !== undefined) {
    if (!Array.isArray(animation)) {
      view.setPauseableAnimation(animation);
    } else {
      view.setPauseableAnimation(...animation);
    }
    map.once('rendercomplete', () => {
      // Decorative pan/zoom: honour prefers-reduced-motion (never
      // resume under it) and support keyboard users via focus events
      // alongside the pointer ones (WCAG 2.3.3/2.2.2).
      const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
      const resume = (): void => {
        if (!reduceMotion.matches) {
          view.resumeAnimation();
        }
      };
      moElement.addEventListener('mouseenter', resume);
      moElement.addEventListener('focusin', resume);
      moElement.addEventListener('mouseleave', () => {
        view.pauseAnimation();
      });
      moElement.addEventListener('focusout', () => {
        view.pauseAnimation();
      });
    });
  }

  return map;
};
