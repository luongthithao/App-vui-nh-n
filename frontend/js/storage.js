export function saveGame(state) {
  localStorage.setItem("bee_game_state", JSON.stringify(state));
}

export function loadGame() {
  const data = localStorage.getItem("bee_game_state");
  if (!data) return null;
  return JSON.parse(data);
}

export function clearGame() {
  localStorage.removeItem("bee_game_state");
}

export function saveScore(score) {
  let scores = JSON.parse(localStorage.getItem("bee_scores") || "[]");

  scores.push(score);
  scores.sort((a, b) => b - a);
  scores = scores.slice(0, 5);

  localStorage.setItem("bee_scores", JSON.stringify(scores));
}

export function loadScores() {
  return JSON.parse(localStorage.getItem("bee_scores") || "[]");
}