export default class SoundManager {
  constructor() {
    this.correct = new Audio("assets/sounds/correct.mp3");
    this.wrong = new Audio("assets/sounds/wrong.mp3");
    this.dice = new Audio("assets/sounds/dice.mp3");
    this.win = new Audio("assets/sounds/win.mp3");

    this.setVolume(0.45);
  }

  setVolume(volume) {
    this.correct.volume = volume;
    this.wrong.volume = volume;
    this.dice.volume = volume;
    this.win.volume = volume;
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