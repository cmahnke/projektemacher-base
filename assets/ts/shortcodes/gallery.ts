import PhotoSwipeLightbox from 'photoswipe/lightbox';
import PhotoSwipe from 'photoswipe';

function photoswipe(id: string, children: string): void {
  const lightbox = new PhotoSwipeLightbox({
    gallery: id,
    children: children,
    showHideAnimationType: 'zoom',
    pswpModule: PhotoSwipe
  });
  lightbox.on('uiRegister', function () {
    const pswp = lightbox.pswp;
    if (!pswp || !pswp.ui) {
      return;
    }
    pswp.ui.registerElement({
      name: 'custom-caption',
      order: 9,
      isButton: false,
      appendTo: 'root',
      html: 'Caption text',
      onInit: (_el) => {
        pswp.on('change', () => {
          const currSlideElement = pswp.currSlide?.data.element as HTMLElement | undefined;
          let captionHTML = '';
          if (currSlideElement) {
            const hiddenCaption = currSlideElement.querySelector<HTMLElement>('.hidden-caption-content');
            if (hiddenCaption) {
              // get caption from element with class hidden-caption-content
              captionHTML = hiddenCaption.innerHTML;
            } else {
              // get caption from alt attribute
              captionHTML = currSlideElement.querySelector('img')?.getAttribute('alt') ?? '';
            }
          }
          _el.innerHTML = captionHTML || '';
        });
      }
    });
  });

  lightbox.init();
}

declare global {
  interface Window {
    photoswipe: typeof photoswipe;
  }
}

window.photoswipe = photoswipe;
