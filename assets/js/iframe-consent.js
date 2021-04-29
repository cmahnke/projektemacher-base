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
    var expire = { expires: 7, path: '' };
    toggle.change(function() {
      if(this.checked) {
          console.log('Setting conset cookie for ' + cookie + ' to true, expire: ' + expire);
          setConsent(cookie, true, expire)
          overlay.hide();
          overlay.after(iframe);
      } else {
          console.log('Setting conset cookie for ' + cookie + ' to false, expire: ' + expire);
          setConsent(cookie, false, expire)
          overlay.show();
          overlay.next().remove();
      }
    });
    if (getConsent(cookie)) {
        toggle.prop('disabled', false);
    }
}
