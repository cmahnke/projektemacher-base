/*
 * Accessible menu enhancement for the theme's checkbox-hack navigation
 * (layouts/partials/menu.html).
 *
 * The markup ships a <label>/<input type="checkbox"> toggle that works
 * without JavaScript. This module - loaded automatically by the menu
 * partial - replaces it with a real <button> once the DOM is ready and
 * takes over state handling:
 *
 *   - aria-expanded / aria-controls on the toggle
 *   - state exposed via data-menu-open on the <nav> (CSS keys off this)
 *   - inert on the closed list - but only while the CSS actually hides
 *     it (mobile regime). An always-visible desktop navigation is never
 *     inerted, and viewport changes re-sync the state.
 *   - Escape closes and returns focus to the toggle
 *   - closes on outside pointerdown and when focus leaves the menu
 *   - stays in sync with the (hidden) checkbox so consumer toggle
 *     customizations keep working
 *
 * Everything is defensive: the module is idempotent, each step is
 * guarded, and the JS-mode marker (data-menu-js) is only set after all
 * wiring succeeded. If anything fails, the untouched checkbox hack
 * remains fully functional.
 */

const NAV_SELECTOR = 'nav.top-menu';

interface MenuLabels {
  open: string;
  close: string;
}

function isOpen(nav: HTMLElement): boolean {
  return nav.getAttribute('data-menu-open') === 'true';
}

function setInert(element: HTMLElement, inert: boolean): void {
  try {
    element.toggleAttribute('inert', inert);
  } catch {
    // toggleAttribute with force is unavailable on very old engines;
    // fall back to explicit attribute handling.
    if (inert) {
      element.setAttribute('inert', '');
    } else {
      element.removeAttribute('inert');
    }
  }
}

function isHiddenByCss(element: HTMLElement): boolean {
  // Detect the mobile regime from the rendered styles instead of a
  // hardcoded media query: the breakpoint is a SCSS value that
  // consumers may override, so a matchMedia width could desync.
  const style = getComputedStyle(element);
  return style.visibility === 'hidden' || style.display === 'none';
}

function resolveCheckbox(nav: HTMLElement, label: HTMLLabelElement | null): HTMLInputElement | null {
  // Prefer the checkbox the label points at, fall back to any checkbox
  // inside the nav (defensive against consumer markup tweaks).
  const forId = label?.htmlFor;
  if (forId) {
    const linked = document.getElementById(forId);
    if (linked instanceof HTMLInputElement && linked.type === 'checkbox') {
      return linked;
    }
  }
  return nav.querySelector<HTMLInputElement>('input[type="checkbox"]');
}

function createToggleButton(
  nav: HTMLElement,
  label: HTMLLabelElement | null,
  list: HTMLElement | null,
  labels: MenuLabels,
): HTMLButtonElement {
  const button = document.createElement('button');
  button.type = 'button';
  if (label) {
    // Preserve the theme's (or a consumer's) classes and icon.
    button.className = label.className;
    while (label.firstChild) {
      button.appendChild(label.firstChild);
    }
  } else {
    button.className = 'menu-button';
  }
  button.setAttribute('aria-expanded', 'false');
  if (list) {
    if (!list.id) {
      list.id = 'main-navigation-list';
    }
    button.setAttribute('aria-controls', list.id);
  }
  button.setAttribute('aria-label', labels.open);
  return button;
}

function enhanceMenu(nav: HTMLElement): void {
  if (nav.dataset.menuEnhanced === 'true') {
    return;
  }
  // Mark early to stay idempotent even if a later step throws; the CSS
  // regime (data-menu-js) is still only activated on full success.
  nav.dataset.menuEnhanced = 'true';

  const label = nav.querySelector<HTMLLabelElement>('label.menu-button');
  const checkbox = resolveCheckbox(nav, label);
  const list = nav.querySelector<HTMLElement>('.navigation-list');
  const labels: MenuLabels = {
    open: nav.dataset.menuOpenLabel || 'Open menu',
    close: nav.dataset.menuCloseLabel || 'Close menu',
  };

  const button = createToggleButton(nav, label, list, labels);
  if (label) {
    label.replaceWith(button);
  } else {
    // No label found - append so the menu stays operable.
    nav.appendChild(button);
  }

  if (checkbox) {
    // Keep the fallback control in the DOM (consumer custom toggles may
    // point at it) but out of the accessibility tree and tab order.
    checkbox.hidden = true;
    checkbox.tabIndex = -1;
  }

  const setOpen = (open: boolean): void => {
    nav.setAttribute('data-menu-open', open ? 'true' : 'false');
    button.setAttribute('aria-expanded', open ? 'true' : 'false');
    button.setAttribute('aria-label', open ? labels.close : labels.open);
    if (list) {
      // Only inert the closed list while the CSS actually hides it
      // (mobile regime). An always-visible desktop menu must stay
      // interactive - inert there would block pointer events and focus.
      setInert(list, !open && isHiddenByCss(list));
    }
  };

  button.addEventListener('click', () => {
    setOpen(!isOpen(nav));
  });

  nav.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && isOpen(nav) && nav.contains(document.activeElement)) {
      setOpen(false);
      button.focus();
    }
  });

  document.addEventListener('pointerdown', (event) => {
    if (isOpen(nav) && event.target instanceof Node && !nav.contains(event.target)) {
      setOpen(false);
    }
  });

  nav.addEventListener('focusout', (event) => {
    if (!isOpen(nav)) {
      return;
    }
    const next = event.relatedTarget;
    if (!(next instanceof Node) || !nav.contains(next)) {
      setOpen(false);
    }
  });

  if (checkbox) {
    checkbox.addEventListener('change', () => {
      setOpen(checkbox.checked);
    });
    if (checkbox.checked) {
      setOpen(true);
    }
  }

  // Keep inert (and the open state) in sync across viewport changes:
  // the mobile regime hides the closed list, the desktop regime shows
  // it. The breakpoint lives in consumer SCSS, so the regime is
  // detected from the rendered styles instead of a matchMedia width.
  let resizeFrame = 0;
  window.addEventListener(
    'resize',
    () => {
      if (resizeFrame) {
        return;
      }
      resizeFrame = requestAnimationFrame(() => {
        resizeFrame = 0;
        if (isOpen(nav) && getComputedStyle(button).display === 'none') {
          // Desktop regime: the toggle is not rendered, so a stale
          // open state would be meaningless - normalize to closed.
          setOpen(false);
        }
        setOpen(isOpen(nav));
      });
    },
    { passive: true },
  );

  // All wiring succeeded - switch the CSS from the checkbox hack to the
  // JS-controlled regime.
  nav.setAttribute('data-menu-js', 'true');
  setOpen(isOpen(nav));
}

function enhanceAllMenus(): void {
  const navs = document.querySelectorAll<HTMLElement>(NAV_SELECTOR);
  navs.forEach((nav) => {
    try {
      enhanceMenu(nav);
    } catch (error) {
      // Never let one broken menu break the page or other scripts.
      console.warn('[menu] enhancement failed, keeping checkbox fallback', error);
    }
  });
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', enhanceAllMenus, { once: true });
} else {
  enhanceAllMenus();
}
