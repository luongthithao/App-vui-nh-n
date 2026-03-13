import Game from "./game.js";

const canvas = document.getElementById("gameCanvas");
const game = new Game(canvas);

document.getElementById("rollDice").onclick = async () => {
  await game.rollDice();
};

document.getElementById("startGame").onclick = () => {
  document.getElementById("startScreen").classList.add("hidden");
};