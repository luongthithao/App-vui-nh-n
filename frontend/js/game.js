import Board from "./board.js";
import Player from "./player.js";
import QuestionUI from "./questionUI.js";
import { getQuestion } from "./api.js";
import AIEngine from "./aiEngine.js";
import { saveGame, loadGame, clearGame } from "./storage.js";
import SoundManager from "./sound.js";

export default class Game {
  constructor(canvas) {
    this.canvas = canvas;
    this.ctx = canvas.getContext("2d");

    this.maxTile = 20;
    this.maxRevives = 3;
    this.maxLevel = 4;

    this.currentLevel = 1;
    this.revives = 3;
    this.score = 0;

    this.board = new Board(canvas);
    this.player = new Player(this.board);
    this.questionUI = new QuestionUI();
    this.ai = new AIEngine();
    this.sound = new SoundManager();

    this.tileQuestions = {};
    this.usedQuestionIds = [];

    this.rollButton = document.getElementById("rollDice");
    this.continueBtn = document.getElementById("continueBtn");
    this.newGameBtn = document.getElementById("newGameBtn");

    this.currentLevelEl = document.getElementById("currentLevel");
    this.currentTileEl = document.getElementById("currentTile");
    this.reviveCountEl = document.getElementById("reviveCount");
    this.diceResultEl = document.getElementById("diceResult");
    this.scoreEl = document.getElementById("score");
    this.aiDifficultyEl = document.getElementById("aiDifficulty");
    this.statusMessageEl = document.getElementById("statusMessage");

    this.levelProgressText = document.getElementById("levelProgressText");
    this.levelProgressFill = document.getElementById("levelProgressFill");

    this.resultOverlay = document.getElementById("resultOverlay");
    this.resultCard = document.getElementById("resultCard");
    this.resultEmoji = document.getElementById("resultEmoji");
    this.resultTitle = document.getElementById("resultTitle");
    this.resultMessage = document.getElementById("resultMessage");
    this.closeResultBtn = document.getElementById("closeResultBtn");

    this.isRolling = false;

    this.closeResultBtn.onclick = () => {
      this.hideResult();
    };

    this.continueBtn.onclick = () => {
      this.startNextLevel();
    };

    this.newGameBtn.onclick = () => {
      this.restartFullGame();
    };

    this.loadState();
    this.player.syncToTile();

    this.updateHUD();
    this.render();

    if (this.player.position >= this.maxTile && this.currentLevel < this.maxLevel) {
      this.continueBtn.classList.remove("hidden");
      this.rollButton.disabled = true;
    }
  }

  async rollDice() {
    if (this.isRolling) return;
    if (this.player.position >= this.maxTile) return;

    this.isRolling = true;
    this.rollButton.disabled = true;
    this.continueBtn.classList.add("hidden");
    this.setStatus("🎲 Đang tung xúc xắc...");

    this.sound.playDice();

    const finalDice = Math.floor(Math.random() * 3) + 1;
    await this.animateDice(finalDice);

    this.setStatus("🐝 Ong đang bay...");
    await this.animatePlayerSteps(finalDice);

    this.updateHUD();
    await this.triggerQuestion();
  }

  animateDice(finalValue) {
    return new Promise((resolve) => {
      let frame = 0;
      const totalFrames = 14;

      const tick = () => {
        frame += 1;
        const tempValue = Math.floor(Math.random() * 6) + 1;
        this.diceResultEl.innerText = `🎲 ${tempValue}`;

        if (frame < totalFrames) {
          setTimeout(tick, 70);
        } else {
          this.diceResultEl.innerText = `🎲 ${finalValue}`;
          resolve();
        }
      };

      tick();
    });
  }

  async animatePlayerSteps(steps) {
    for (let i = 0; i < steps; i += 1) {
      if (this.player.position >= this.maxTile) break;

      this.player.move(1);
      const targetTile = this.board.getTilePosition(this.player.position);

      await this.player.animateToTile(targetTile, 280);
      this.render();
      this.updateHUD();
    }
  }

  async triggerQuestion() {
    try {
      const tile = this.player.position;
      const subject = this.getSubject(tile);
      const difficulty = this.getDifficultyForTile(tile, this.currentLevel);

      let question;

      if (this.tileQuestions[tile]) {
        question = this.tileQuestions[tile];
      } else {
        question = await getQuestion(subject, difficulty, this.usedQuestionIds);
        this.tileQuestions[tile] = question;
      }

      this.questionUI.show(
        {
          subject,
          difficulty,
          text: question.text,
          options: question.options,
          answer: question.answer
        },
        (correct) => {
          this.handleAnswer(correct);
        }
      );
    } catch (error) {
      console.error(error);
      this.setStatus("Không còn đủ câu hỏi mới cho level này.");
      this.isRolling = false;
      this.rollButton.disabled = false;
    }
  }

  handleAnswer(correct) {
    this.ai.recordResult(correct);

    const tile = this.player.position;
    const currentQuestion = this.tileQuestions[tile];

    if (correct) {
      if (currentQuestion && !this.usedQuestionIds.includes(currentQuestion.id)) {
        this.usedQuestionIds.push(currentQuestion.id);
      }

      delete this.tileQuestions[tile];
      this.score += 10;
      this.sound.playCorrect();
      this.setStatus("✅ Đúng rồi! +10 điểm");
      this.questionUI.clear();

      if (this.player.position >= this.maxTile) {
        if (this.currentLevel < this.maxLevel) {
          this.sound.playWin();
          this.showLevelCompleteResult();
          this.continueBtn.classList.remove("hidden");
          this.rollButton.disabled = true;
          this.isRolling = false;
        } else {
          this.sound.playWin();
          this.showFinalWinResult();
          this.rollButton.disabled = true;
          this.isRolling = true;
        }
      } else {
        this.isRolling = false;
        this.rollButton.disabled = false;
      }
    } else {
      this.revives -= 1;
      this.sound.playWrong();

      if (this.revives > 0) {
        this.setStatus(`❌ Sai rồi. Em còn ${this.revives} lượt hồi sinh.`);
        this.showLoseResult(false);
        this.isRolling = false;
        this.rollButton.disabled = false;
      } else {
        this.setStatus("💥 Hết lượt hồi sinh. Quay về level 1!");
        this.player.reset();
        this.score = 0;
        this.revives = this.maxRevives;
        this.currentLevel = 1;
        this.tileQuestions = {};
        this.usedQuestionIds = [];
        this.questionUI.clear();
        this.showLoseResult(true);
        this.isRolling = false;
        this.rollButton.disabled = false;
      }
    }

    this.saveState();
    this.updateHUD();
    this.render();
  }

  getDifficultyForTile(tile, level) {
    if (level === 1) return "easy";

    if (level === 2) {
      if (tile <= 6) return "easy";
      return "medium";
    }

    if (level === 3) {
      if (tile <= 5) return "medium";
      return "hard";
    }

    if (tile <= 4) return "medium";
    return "hard";
  }

  showLevelCompleteResult() {
    this.resultCard.className = "result-card win";
    this.resultEmoji.innerText = "⭐";
    this.resultTitle.innerText = `Hoàn thành Level ${this.currentLevel}`;
    this.resultMessage.innerText =
      `Rất tốt! Em đã hoàn thành 20 câu của level ${this.currentLevel}. Bấm "Chơi tiếp level sau" để sang level khó hơn.`;

    this.closeResultBtn.innerText = "Đóng";
    this.resultOverlay.classList.remove("hidden");
  }

  showFinalWinResult() {
    this.resultCard.className = "result-card win";
    this.resultEmoji.innerText = "🏆";
    this.resultTitle.innerText = "Hoàn thành toàn bộ thử thách!";
    this.resultMessage.innerText =
      `Em đã vượt qua 4 level với tổng ${this.score} điểm. Quá xuất sắc!`;

    this.closeResultBtn.innerText = "Chơi lại từ đầu";
    this.closeResultBtn.onclick = () => {
      this.restartFullGame();
    };

    this.resultOverlay.classList.remove("hidden");
  }

  showLoseResult(isResetToStart) {
    this.resultCard.className = "result-card lose";
    this.resultEmoji.innerText = isResetToStart ? "💥" : "😵";
    this.resultTitle.innerText = isResetToStart ? "Hết lượt hồi sinh" : "Trả lời sai";
    this.resultMessage.innerText = isResetToStart
      ? "Em đã quay về level 1. Hãy thử lại từ đầu nhé!"
      : "Không sao, em vẫn còn cơ hội để tiếp tục.";

    this.closeResultBtn.innerText = "Tiếp tục";
    this.closeResultBtn.onclick = () => {
      this.hideResult();
    };

    this.resultOverlay.classList.remove("hidden");
  }

  startNextLevel() {
    if (this.currentLevel >= this.maxLevel) return;

    this.hideResult();

    this.currentLevel += 1;
    this.player.reset();
    this.revives = this.maxRevives;
    this.tileQuestions = {};
    this.isRolling = false;

    this.rollButton.disabled = false;
    this.continueBtn.classList.add("hidden");

    this.questionUI.clear();
    this.setStatus(`🚀 Bắt đầu Level ${this.currentLevel}! Câu hỏi sẽ khó hơn.`);
    this.saveState();
    this.updateHUD();
    this.render();
  }

  restartFullGame() {
    this.hideResult();

    this.currentLevel = 1;
    this.revives = this.maxRevives;
    this.score = 0;
    this.tileQuestions = {};
    this.usedQuestionIds = [];
    this.player.reset();
    this.questionUI.clear();

    this.isRolling = false;
    this.rollButton.disabled = false;
    this.continueBtn.classList.add("hidden");

    clearGame();
    this.saveState();
    this.updateHUD();
    this.render();
    this.setStatus("Bắt đầu lại từ level 1!");
  }

  hideResult() {
    this.resultOverlay.classList.add("hidden");
  }

  saveState() {
    saveGame({
      currentLevel: this.currentLevel,
      position: this.player.position,
      revives: this.revives,
      score: this.score,
      questions: this.tileQuestions,
      usedQuestionIds: this.usedQuestionIds
    });
  }

  loadState() {
    const data = loadGame();
    if (!data) return;

    this.currentLevel = data.currentLevel || 1;
    this.player.position = data.position || 1;
    this.revives = data.revives || 3;
    this.score = data.score || 0;
    this.tileQuestions = data.questions || {};
    this.usedQuestionIds = data.usedQuestionIds || [];
  }

  getSubject(tile) {
    if (tile % 3 === 0) return "math";
    if (tile % 3 === 1) return "english";
    return "vietnamese";
  }

  updateHUD() {
    this.currentLevelEl.innerText = `${this.currentLevel}`;
    this.currentTileEl.innerText = `${this.player.position} / ${this.maxTile}`;
    this.reviveCountEl.innerText = `${this.revives}`;
    this.scoreEl.innerText = `${this.score}`;
    this.aiDifficultyEl.innerText = this.ai.getDifficulty();

    this.levelProgressText.innerText = `${this.player.position} / ${this.maxTile}`;
    const progress = (this.player.position / this.maxTile) * 100;
    this.levelProgressFill.style.width = `${progress}%`;
  }

  setStatus(message) {
    this.statusMessageEl.innerText = message;
  }

  render() {
    this.board.draw(this.player.position);
    this.player.draw(this.ctx);
  }
}