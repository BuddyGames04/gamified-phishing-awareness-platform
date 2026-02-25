let audio: HTMLAudioElement | null = null;

export function primeWaveAudio() {
  if (!audio) {
    audio = new Audio('/sfx/new-mail.mp3');
    audio.volume = 0.6;
  }
}

export async function playWaveChime() {
  try {
    if (!audio) primeWaveAudio();
    await audio?.play();
  } catch {
    // ignore (autoplay restrictions, user muted, etc.)
  }
}
