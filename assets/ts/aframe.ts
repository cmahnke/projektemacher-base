/*
 * A-Frame runtime for the `aframe-3d-model` shortcode.
 * Replaces the former CDN scripts (aframe.io release bundle + unpkg
 * aframe-orbit-controls) with the npm packages pinned in package.json.
 *
 * aframe-orbit-controls is a plain script that registers itself on the
 * global AFRAME object and does not import 'aframe' as a peer dependency,
 * so the global must be in place before the component registers. Static
 * imports are hoisted, hence the dynamic import below.
 */
import AFRAME from 'aframe';

(window as unknown as { AFRAME: unknown }).AFRAME = AFRAME;

import('aframe-orbit-controls');
