import { Howl } from 'howler';

function audioplayer(elem: HTMLElement, src: string, btn: HTMLButtonElement): void {
  const sound = new Howl({
    html5: true,
    src: [src],
    onend(): void {
      btn.classList.add('play');
      btn.classList.remove('pause');
      elem.removeEventListener('click', play);
      elem.addEventListener('click', play);
    },
    onpause(): void {
      btn.classList.add('play');
      btn.classList.remove('pause');
      elem.removeEventListener('click', pause);
      elem.addEventListener('click', play);
    },
    onstop(): void {
      btn.classList.remove('pause');
      btn.classList.add('play');
      elem.removeEventListener('click', pause);
      elem.addEventListener('click', play);
    },
    onplay(): void {
      btn.classList.remove('play');
      btn.classList.add('pause');
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

  elem.addEventListener('click', play);
}

window.audioplayer = audioplayer;
