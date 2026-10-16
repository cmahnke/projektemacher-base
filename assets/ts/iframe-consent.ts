import Cookies from 'js-cookie';

function getConsent(cookie: string): boolean {
  Cookies.get(cookie);
  if (cookie != null && cookie == '1') {
    return true;
  }
  return false;
}

function setConsent(cookie: string, consent: boolean, expire: object): void {
  // js-cookie stringifies values at runtime, but its types only allow strings
  Cookies.set(cookie, consent as unknown as string, expire);
}

export function addConsent(
  toggle: HTMLInputElement,
  overlay: HTMLElement,
  cookie: string,
  iframe: string,
): void {
  let expire: object = { expires: 30, path: '' };
  expire = Object.assign(expire, { sameSite: 'None', secure: true });

  toggle.addEventListener('change', function () {
    if (this.checked) {
      console.log('Setting conset cookie for ' + cookie + ' to true, expire: ' + expire);
      setConsent(cookie, true, expire);
      overlay.style.display = 'none';
      const content = overlay.parentNode?.querySelector('.iframe-content');
      if (content) {
        content.innerHTML = iframe;
        Array.from(overlay.parentNode?.querySelectorAll('.iframe-content script') ?? []).forEach(
          (el) => eval(el.innerHTML),
        );
      }
    } else {
      console.log('Setting conset cookie for ' + cookie + ' to false, expire: ' + expire);
      setConsent(cookie, false, expire);
      overlay.style.display = 'block';
      Array.from(overlay.parentNode?.querySelectorAll('.iframe-content *') ?? []).forEach((el) =>
        el.remove(),
      );
    }
  });

  if (getConsent(cookie)) {
    toggle.disabled = false;
  }
}

window.addConsent = addConsent;
