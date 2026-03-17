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
    this.stageReward = 30;

    this.currentStage = 1;
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

    if (this.closeResultBtn) {
      this.closeResultBtn.onclick = () => {
        this.hideResult();
      };
    }

    if (this.continueBtn) {
      this.continueBtn.onclick = () => {
        this.startNextStage();
      };
    }

    if (this.newGameBtn) {
      this.newGameBtn.onclick = () => {
        this.restartFullGame();
      };
    }

    this.loadState();
    this.player.syncToTile();

    this.updateHUD();
    this.render();

    if (this.player.position >= this.maxTile) {
      if (this.continueBtn) this.continueBtn.classList.remove("hidden");
      if (this.rollButton) this.rollButton.disabled = true;
    }
  }

  async rollDice() {
    if (this.isRolling) return;
    if (this.player.position >= this.maxTile) return;

    this.isRolling = true;
    this.rollButton.disabled = true;

    if (this.continueBtn) {
      this.continueBtn.classList.add("hidden");
    }

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
      const totalFrames = 16;

      const tick = () => {
        frame += 1;
        const tempValue = Math.floor(Math.random() * 6) + 1;
        this.diceResultEl.innerText = `🎲 ${tempValue}`;

        if (frame < totalFrames) {
          setTimeout(tick, 65);
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
      const difficulty = this.getDifficultyForStage(tile, this.currentStage);

      let question;

      this.questionUI.showLoading();

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
      this.setStatus("Màn này đang thiếu câu mới ở mức độ khó hiện tại.");
      this.questionUI.clear();
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
        this.score += this.stageReward;
        this.sound.playWin();
        this.showStageCompleteResult();

        if (this.continueBtn) {
          this.continueBtn.classList.remove("hidden");
        }

        this.rollButton.disabled = true;
        this.isRolling = false;
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
        this.setStatus(`💥 Hết lượt hồi sinh. Quay lại đầu màn ${this.currentStage}!`);
        this.player.reset();
        this.revives = this.maxRevives;
        this.tileQuestions = {};
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

  getDifficultyForStage(tile, stage) {
    let base;

    if (stage <= 3) {
      base = "easy";
    } else if (stage <= 6) {
      base = tile <= 10 ? "easy" : "medium";
    } else if (stage <= 10) {
      base = "medium";
    } else if (stage <= 15) {
      base = tile <= 6 ? "medium" : "hard";
    } else {
      base = "hard";
    }

    const aiLevel = this.ai.getDifficulty();

    if (base === "easy" && aiLevel === "hard") return "medium";
    if (base === "medium" && aiLevel === "easy") return "easy";
    if (base === "medium" && aiLevel === "hard") return "hard";
    if (base === "hard" && aiLevel === "easy") return "medium";

    return base;
  }

  showStageCompleteResult() {
    if (!this.resultOverlay) return;

    this.resultCard.className = "result-card win";
    this.resultEmoji.innerText = "⭐";
    this.resultTitle.innerText = `Hoàn thành màn ${this.currentStage}`;
    this.resultMessage.innerText =
      `Rất tốt! Em đã hoàn thành màn ${this.currentStage} và nhận thêm ${this.stageReward} điểm thưởng. Bấm "Qua màn tiếp theo" để đi tiếp.`;

    this.closeResultBtn.innerText = "Đóng";
    this.resultOverlay.classList.remove("hidden");
  }

  showLoseResult(isResetToStart) {
    if (!this.resultOverlay) return;

    this.resultCard.className = "result-card lose";
    this.resultEmoji.innerText = isResetToStart ? "💥" : "😵";
    this.resultTitle.innerText = isResetToStart ? "Hết lượt hồi sinh" : "Trả lời sai";
    this.resultMessage.innerText = isResetToStart
      ? `Em quay lại ô số 1 của màn ${this.currentStage}. Tiếp tục cố gắng nhé!`
      : "Không sao, em vẫn còn cơ hội để tiếp tục.";

    this.closeResultBtn.innerText = "Tiếp tục";
    this.closeResultBtn.onclick = () => {
      this.hideResult();
    };

    this.resultOverlay.classList.remove("hidden");
  }

  startNextStage() {
    this.hideResult();

    this.currentStage += 1;
    this.player.reset();
    this.revives = this.maxRevives;
    this.tileQuestions = {};
    this.isRolling = false;

    this.rollButton.disabled = false;

    if (this.continueBtn) {
      this.continueBtn.classList.add("hidden");
    }

    this.questionUI.clear();
    this.setStatus(`🚀 Bắt đầu màn ${this.currentStage}! Câu hỏi sẽ khó hơn.`);
    this.saveState();
    this.updateHUD();
    this.render();
  }

  restartFullGame() {
    this.hideResult();

    this.currentStage = 1;
    this.revives = this.maxRevives;
    this.score = 0;
    this.tileQuestions = {};
    this.usedQuestionIds = [];
    this.player.reset();
    this.questionUI.clear();

    this.isRolling = false;
    this.rollButton.disabled = false;

    if (this.continueBtn) {
      this.continueBtn.classList.add("hidden");
    }

    clearGame();
    this.saveState();
    this.updateHUD();
    this.render();
    this.setStatus("Bắt đầu lại từ màn 1!");
  }

  hideResult() {
    if (this.resultOverlay) {
      this.resultOverlay.classList.add("hidden");
    }
  }

  saveState() {
    saveGame({
      currentStage: this.currentStage,
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

    this.currentStage = data.currentStage || 1;
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
    if (this.currentLevelEl) {
      this.currentLevelEl.innerText = `${this.currentStage}`;
    }

    if (this.currentTileEl) {
      this.currentTileEl.innerText = `${this.player.position} / ${this.maxTile}`;
    }

    if (this.reviveCountEl) {
      this.reviveCountEl.innerText = `${this.revives}`;
    }

    if (this.scoreEl) {
      this.scoreEl.innerText = `${this.score}`;
    }

    if (this.aiDifficultyEl) {
      this.aiDifficultyEl.innerText = this.ai.getDifficulty();
    }

    if (this.levelProgressText) {
      this.levelProgressText.innerText = `${this.player.position} / ${this.maxTile}`;
    }

    if (this.levelProgressFill) {
      const progress = (this.player.position / this.maxTile) * 100;
      this.levelProgressFill.style.width = `${progress}%`;
    }
  }

  setStatus(message) {
    if (this.statusMessageEl) {
      this.statusMessageEl.innerText = message;
    }
  }

  render() {
    this.board.draw(this.player.position);
    this.player.draw(this.ctx);
  }
}