import { Howl } from 'howler';

/*
 * Sync the visual icon and the announced state (WCAG 4.1.2): the
 * button exposes its pressed state via `aria-pressed` and swaps the
 * label between the play and pause strings the shortcode puts into
 * data attributes.
 */
function setPlaying(btn: HTMLButtonElement, playing: boolean): void {
  btn.classList.toggle('play', !playing);
  btn.classList.toggle('pause', playing);
  btn.setAttribute('aria-pressed', playing ? 'true' : 'false');
  const label = playing ? btn.dataset.pauseLabel : btn.dataset.playLabel;
  if (label) {
    btn.setAttribute('aria-label', label);
  }
}

function audioplayer(elem: HTMLElement, src: string, btn: HTMLButtonElement): void {
  const sound = new Howl({
    html5: true,
    src: [src],
    onend(): void {
      setPlaying(btn, false);
      elem.removeEventListener('click', pause);
      elem.addEventListener('click', play);
    },
    onpause(): void {
      setPlaying(btn, false);
      elem.removeEventListener('click', pause);
      elem.addEventListener('click', play);
    },
    onstop(): void {
      setPlaying(btn, false);
      elem.removeEventListener('click', pause);
      elem.addEventListener('click', play);
    },
    onplay(): void {
      setPlaying(btn, true);
      elem.removeEventListener('click', play);
      elem.addEventListener('click', pause);
    },
  });

  function play(): void {
    sound.play();
  }

  function pause(): void {
    sound.pause();
  }

  setPlaying(btn, false);
  elem.addEventListener('click', play);
}

window.audioplayer = audioplayer;
