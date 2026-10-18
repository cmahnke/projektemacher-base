import Cookies from 'js-cookie';

/*
 * iframe consent ("opt-in") handling for the theme's checkbox-hack
 * switch (layouts/partials/html/iframe-consent.html).
 *
 * addConsent() is called once per embedded iframe by an inline script
 * emitted by the partial. It wires the fallback checkbox and - following
 * the progressive enhancement pattern of the navigation menu
 * (assets/ts/menu.ts) - replaces the <label> hack with a real
 * <button role="switch">:
 *
 *   - keyboard operable (the visually hidden fallback checkbox is not
 *     removed from the tab order, but the button is the primary control)
 *   - aria-checked exposes the state to assistive technology
 *   - the hidden checkbox stays in the DOM and remains the state source,
 *     so consumer code binding to it keeps working
 *
 * Everything is defensive: the module is idempotent and a failure keeps
 * the (visually hidden but focusable) checkbox fallback functional.
 */

function getConsent(cookie: string): boolean {
  return Cookies.get(cookie) === '1';
}

function setConsent(cookie: string, consent: boolean, expire: object): void {
  // js-cookie stringifies values at runtime, but its types only allow strings
  Cookies.set(cookie, consent as unknown as string, expire);
}

function createSwitchButton(toggle: HTMLInputElement): HTMLButtonElement {
  const button = document.createElement('button');
  button.type = 'button';
  // Same class as the fallback label, so the switch styles apply.
  button.className = 'opt-in-switch';
  button.setAttribute('role', 'switch');
  button.setAttribute('aria-checked', toggle.checked ? 'true' : 'false');
  const labelledBy = toggle.getAttribute('aria-labelledby');
  if (labelledBy) {
    button.setAttribute('aria-labelledby', labelledBy);
  }
  const slider = document.createElement('span');
  slider.className = 'opt-in-slider';
  slider.setAttribute('aria-hidden', 'true');
  button.appendChild(slider);
  return button;
}

function enhanceSwitch(toggle: HTMLInputElement): void {
  const label = toggle.closest<HTMLElement>('label.opt-in-switch');
  const wrapper = label?.parentElement;
  if (!label || !wrapper) {
    // Already enhanced or consumer restructured the markup.
    return;
  }
  const button = createSwitchButton(toggle);
  // Detach the checkbox from the label before replacing it, so the
  // state source stays in the DOM.
  wrapper.insertBefore(toggle, label);
  label.replaceWith(button);
  toggle.hidden = true;
  toggle.tabIndex = -1;

  button.addEventListener('click', () => {
    toggle.checked = !toggle.checked;
    toggle.dispatchEvent(new Event('change', { bubbles: true }));
  });

  toggle.addEventListener('change', () => {
    button.setAttribute('aria-checked', toggle.checked ? 'true' : 'false');
  });
}

export function addConsent(
  toggle: HTMLInputElement,
  overlay: HTMLElement,
  cookie: string,
  iframe: string,
): void {
  if (toggle.dataset.consentWired === 'true') {
    return;
  }
  toggle.dataset.consentWired = 'true';

  const expire: object = { expires: 30, path: '', sameSite: 'None', secure: true };

  const accept = (): void => {
    console.log('Setting consent cookie for ' + cookie + ' to true');
    setConsent(cookie, true, expire);
    overlay.style.display = 'none';
    const content = overlay.parentNode?.querySelector('.iframe-content');
    if (content) {
      content.innerHTML = iframe;
      Array.from(overlay.parentNode?.querySelectorAll('.iframe-content script') ?? []).forEach(
        (el) => eval(el.innerHTML),
      );
    }
  };

  const deny = (): void => {
    console.log('Setting consent cookie for ' + cookie + ' to false');
    setConsent(cookie, false, expire);
    overlay.style.display = 'block';
    Array.from(overlay.parentNode?.querySelectorAll('.iframe-content *') ?? []).forEach((el) =>
      el.remove(),
    );
  };

  toggle.addEventListener('change', () => {
    if (toggle.checked) {
      accept();
    } else {
      deny();
    }
  });

  enhanceSwitch(toggle);

  // Returning visitor with a stored consent: reflect the state and load
  // the embedded content (the change handler does both).
  if (getConsent(cookie)) {
    toggle.checked = true;
    toggle.dispatchEvent(new Event('change', { bubbles: true }));
  }
}

window.addConsent = addConsent;
