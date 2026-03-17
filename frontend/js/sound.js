export default class SoundManager {
  constructor() {
    this.correct = this.createAudio("assets/sounds/correct.mp3");
    this.wrong = this.createAudio("assets/sounds/wrong.mp3");
    this.dice = this.createAudio("assets/sounds/dice.mp3");
    this.win = this.createAudio("assets/sounds/win.mp3");

    this.setVolume(0.45);
  }

  createAudio(src) {
    const audio = new Audio();
    audio.src = src;
    audio.preload = "auto";

    audio.addEventListener("error", () => {
      console.warn(`Không tải được âm thanh: ${src}`);
    });

    return audio;
  }

  setVolume(volume) {
    [this.correct, this.wrong, this.dice, this.win].forEach((audio) => {
      if (audio) {
        audio.volume = volume;
      }
    });
  }

  play(audio) {
    if (!audio) return;

    try {
      audio.pause();
      audio.currentTime = 0;

      const promise = audio.play();
      if (promise && typeof promise.catch === "function") {
        promise.catch(() => {});
      }
    } catch (error) {
      console.warn("Play sound error:", error);
    }
  }

  playCorrect() {
    this.play(this.correct);
  }

  playWrong() {
    this.play(this.wrong);
  }

  playDice() {
    this.play(this.dice);
  }

  playWin() {
    this.play(this.win);
  }
}