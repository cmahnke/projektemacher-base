const {Howl, Howler} = require('howler');

function audioplayer (elem, src, btn) {

    var sound = new Howl({
      html5: true,
      src: [src],
      onend: function() {
          btn.classList.add("play");
          btn.classList.remove("pause");
          elem.removeEventListener("click", play);
          elem.addEventListener("click", play);
      },
      onpause: function() {
          btn.classList.add("play");
          btn.classList.remove("pause");
          elem.removeEventListener("click", pause);
          elem.addEventListener("click", play);
      },
      onstop: function() {
          btn.classList.remove("pause");
          btn.classList.add("play");
          elem.removeEventListener("click", pause);
          elem.addEventListener("click", play);
      },
      onplay: function() {
        btn.classList.remove("play");
        btn.classList.add("pause");
        elem.removeEventListener("click", play);
        elem.addEventListener("click", pause);
      }
    });
    function play() {
        sound.play();
    }
    function pause() {
        sound.pause();
    }
    elem.addEventListener("click", play);

}


window.audioplayer =  audioplayer
