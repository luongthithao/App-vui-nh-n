const GAME_KEY = "bee_game_state";
const SCORE_KEY = "bee_scores";

export function saveGame(state) {
  localStorage.setItem(GAME_KEY, JSON.stringify(state));
}

export function loadGame() {
  const data = localStorage.getItem(GAME_KEY);
  if (!data) return null;

  try {
    return JSON.parse(data);
  } catch (error) {
    console.error("Load game error:", error);
    return null;
  }
}

export function clearGame() {
  localStorage.removeItem(GAME_KEY);
}

export function hasSavedGame() {
  return !!localStorage.getItem(GAME_KEY);
}

export function saveScore(score) {
  let scores = [];

  try {
    scores = JSON.parse(localStorage.getItem(SCORE_KEY) || "[]");
  } catch (_) {
    scores = [];
  }

  scores.push(score);
  scores.sort((a, b) => b - a);
  scores = scores.slice(0, 5);

  localStorage.setItem(SCORE_KEY, JSON.stringify(scores));
}

export function loadScores() {
  try {
    return JSON.parse(localStorage.getItem(SCORE_KEY) || "[]");
  } catch (_) {
    return [];
  }
}