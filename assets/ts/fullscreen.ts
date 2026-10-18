/*
 * Fullscreen toggle helper for the theme's html-body template
 * (layouts/_default/html-body.html renders #fullscreen-button and
 * #fullscreen-context).
 *
 * The theme does NOT wire the button automatically - consuming sites
 * opt in by loading this bundle (page front matter `js:` entry) and
 * calling:
 *
 *   window.addFSToggle(
 *     document.getElementById('fullscreen-button'),
 *     document.getElementById('fullscreen-context'),
 *   );
 *
 * Compared to the retired assets/js/fullscreen.js shim the helper now
 * syncs `aria-pressed` on the button and listens for
 * `fullscreenchange`, so leaving fullscreen via Escape or the browser
 * UI resets the button state and styles as well (WCAG 4.1.2 - state
 * is no longer stale).
 */

function enterMode(button: HTMLButtonElement, elem: HTMLElement): void {
  const fsStyle =
    'position: fixed; top: 0; left: 0; height: 100%; width: 100%; overflow: hidden;';
  elem.setAttribute('style', fsStyle);
  button.setAttribute('style', 'position: fixed;');
  button.classList.add('close');
  document.querySelector('body')?.setAttribute('style', 'overflow: hidden;');
}

function exitMode(button: HTMLButtonElement, elem: HTMLElement): void {
  elem.setAttribute('style', '');
  button.setAttribute('style', '');
  button.classList.remove('close');
  document.querySelector('body')?.setAttribute('style', '');
}

function addFSToggle(button: HTMLButtonElement, elem: HTMLElement): void {
  if (button.dataset.fsToggleWired === 'true') {
    return;
  }
  button.dataset.fsToggleWired = 'true';

  const setPressed = (pressed: boolean): void => {
    button.setAttribute('aria-pressed', pressed ? 'true' : 'false');
  };

  button.addEventListener('click', () => {
    if (!document.fullscreenElement) {
      enterMode(button, elem);
      setPressed(true);
      document.documentElement.requestFullscreen();
    } else if (document.exitFullscreen) {
      document.exitFullscreen();
    }
  });

  // Covers every exit path (Escape, browser UI, our own button), so
  // the visual and announced state never go stale.
  document.addEventListener('fullscreenchange', () => {
    if (!document.fullscreenElement) {
      exitMode(button, elem);
    }
    setPressed(document.fullscreenElement != null);
  });
}

window.addFSToggle = addFSToggle;
