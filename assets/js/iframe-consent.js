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
        Cookies.set(cookie, '1', { expires: expire });
    } else {
        Cookies.set(cookie, '0', { expires: expire });
    }
}

export function addConsent(toggle, overlay, cookie, iframe) {
    var expire = { expires: 7, path: '' };
    toggle.change(function() {
      if(this.checked) {
          console.log('Setting conset cookie for ' + cookie + ' to true');
          setConsent(cookie, true, expire)
          overlay.hide();
          overlay.after(iframe);
      } else {
          console.log('Setting conset cookie for ' + cookie + ' to false');
          setConsent(cookie, false, expire)
          overlay.show();
          overlay.next().remove();
      }
    });
    if (getConsent(cookie)) {
        toggle.prop('disabled', false);
    }
}
