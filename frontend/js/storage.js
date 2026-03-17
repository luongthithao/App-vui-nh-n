const GAME_KEY = "bee_game_state";
const SCORE_KEY = "bee_scores";

export function saveGame(state) {
  try {
    localStorage.setItem(GAME_KEY, JSON.stringify(state));
  } catch (error) {
    console.error("Save game error:", error);
  }
}

export function loadGame() {
  const raw = localStorage.getItem(GAME_KEY);
  if (!raw) return null;

  try {
    return JSON.parse(raw);
  } catch (error) {
    console.error("Load game error:", error);
    return null;
  }
}

export function clearGame() {
  try {
    localStorage.removeItem(GAME_KEY);
  } catch (error) {
    console.error("Clear game error:", error);
  }
}

export function saveScore(score) {
  try {
    let scores = JSON.parse(localStorage.getItem(SCORE_KEY) || "[]");

    scores.push(score);
    scores.sort((a, b) => b - a);
    scores = scores.slice(0, 5);

    localStorage.setItem(SCORE_KEY, JSON.stringify(scores));
  } catch (error) {
    console.error("Save score error:", error);
  }
}

export function loadScores() {
  try {
    return JSON.parse(localStorage.getItem(SCORE_KEY) || "[]");
  } catch (error) {
    console.error("Load scores error:", error);
    return [];
  }
}