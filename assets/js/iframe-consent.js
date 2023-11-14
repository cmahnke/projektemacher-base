import Cookies from 'js-cookie'

function getConsent(cookie) {
  Cookies.get(cookie);
  if (cookie != null && cookie == '1') {
    return true;
  }
  return false;
}

function setConsent(cookie, consent, expire) {
  if (consent == true) {
    Cookies.set(cookie, true, expire);
  } else {
    Cookies.set(cookie, false, expire);
  }
}

export function addConsent(toggle, overlay, cookie, iframe) {
  var expire = { expires: 30, path: '' };
  expire = Object.assign(expire, {sameSite: 'None', secure: true});

  toggle.addEventListener('change', function() {
    if(this.checked) {
      console.log('Setting conset cookie for ' + cookie + ' to true, expire: ' + expire);
      setConsent(cookie, true, expire)
      overlay.style.display = 'none';
      overlay.parentNode.querySelector('.iframe-content').innerHTML = iframe;
      Array.from(overlay.parentNode.querySelectorAll('.iframe-content script')).forEach(el => eval(el.innerHTML));
    } else {
      console.log('Setting conset cookie for ' + cookie + ' to false, expire: ' + expire);
      setConsent(cookie, false, expire)
      overlay.style.display = 'block';
      Array.from(overlay.parentNode.querySelectorAll('.iframe-content *')).forEach(el => el.remove());
    }
  });
  if (getConsent(cookie)) {
    toggle.disabled = false;
  }
}
