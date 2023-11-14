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
      /* TODO: This seems to be wrong
         overlay.parentNode.insertAdjacentHTML("afterEnd", iframe);
      */
      //overlay.parentNode.appendChild(iframe);
      overlay.parentNode.insertAdjacentHTML("afterEnd", iframe);
    } else {
      console.log('Setting conset cookie for ' + cookie + ' to false, expire: ' + expire);
      setConsent(cookie, false, expire)
      overlay.style.display = 'block';
      overlay.nextSibling.remove();
    }
  });
  if (getConsent(cookie)) {
    toggle.disabled = false;
  }
}
