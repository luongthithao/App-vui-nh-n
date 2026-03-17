import Game from "./game.js";
import { hasSavedGame } from "./storage.js";

const canvas = document.getElementById("gameCanvas");
const game = new Game(canvas);

const rollDiceBtn = document.getElementById("rollDice");
const startGameBtn = document.getElementById("startGame");
const startScreen = document.getElementById("startScreen");

if (rollDiceBtn) {
  rollDiceBtn.onclick = async () => {
    await game.rollDice();
  };
}

if (startGameBtn) {
  if (hasSavedGame()) {
    startGameBtn.innerText = "🚀 Vào game / chơi tiếp";
  }

  startGameBtn.onclick = () => {
    startScreen.classList.add("hidden");
    game.render();
  };
}