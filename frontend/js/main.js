import Game from "./game.js";

const canvas = document.getElementById("gameCanvas");
const game = new Game(canvas);

const rollDiceBtn = document.getElementById("rollDice");
const startGameBtn = document.getElementById("startGame");
const startScreen = document.getElementById("startScreen");
const playerNameInput = document.getElementById("playerName");
const avatarSelect = document.getElementById("avatarSelect");
const previewAvatar = document.getElementById("previewAvatar");
const startError = document.getElementById("startError");

function setStartError(message = "") {
  if (!startError) return;
  startError.innerText = message;
  startError.classList.toggle("hidden", !message);
}

function updateStartButtonState() {
  if (!startGameBtn || !playerNameInput) return;

  const hasName = playerNameInput.value.trim().length > 0;
  startGameBtn.disabled = !hasName;

  if (hasName) {
    playerNameInput.classList.remove("input-error");
    setStartError("");
  }
}

if (rollDiceBtn) {
  rollDiceBtn.onclick = async () => {
    await game.rollDice();
  };
}

if (avatarSelect && previewAvatar) {
  previewAvatar.innerText = avatarSelect.value || "🐝";

  avatarSelect.addEventListener("change", () => {
    previewAvatar.innerText = avatarSelect.value || "🐝";
  });
}

if (playerNameInput) {
  playerNameInput.addEventListener("input", () => {
    updateStartButtonState();
  });

  playerNameInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      event.preventDefault();
      if (!startGameBtn.disabled) {
        startGameBtn.click();
      }
    }
  });
}

if (startGameBtn) {
  startGameBtn.addEventListener("click", (event) => {
    event.preventDefault();

    const playerName = playerNameInput ? playerNameInput.value.trim() : "";
    const avatar = avatarSelect ? avatarSelect.value : "🐝";

    if (!playerName) {
      if (playerNameInput) {
        playerNameInput.focus();
        playerNameInput.classList.add("input-error");
      }
      setStartError("Vui lòng nhập tên người chơi.");
      return;
    }

    game.setProfile(playerName, avatar);

    if (startScreen) {
      startScreen.classList.add("hidden");
    }

    game.render();
  });

  updateStartButtonState();
}