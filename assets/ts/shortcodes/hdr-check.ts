import { checkHDR, checkHDRCanvas } from '@projektemacher/hdr-canvas';

declare global {
  interface Window {
    checkHDR: typeof checkHDR;
    checkHDRCanvas: typeof checkHDRCanvas;
  }
}

window.checkHDR = checkHDR;
window.checkHDRCanvas = checkHDRCanvas;
