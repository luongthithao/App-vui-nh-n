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
    audio.preload = "none";
    return audio;
  }

  setVolume(volume) {
    if (this.correct) this.correct.volume = volume;
    if (this.wrong) this.wrong.volume = volume;
    if (this.dice) this.dice.volume = volume;
    if (this.win) this.win.volume = volume;
  }

  play(audio) {
    if (!audio) return;

    audio.pause();
    audio.currentTime = 0;
    audio.play().catch(() => {});
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