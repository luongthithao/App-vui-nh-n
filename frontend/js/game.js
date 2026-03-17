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
    this.revives = this.maxRevives;
    this.score = 0;
    this.playerName = "Người chơi";
    this.avatar = "🐝";

    this.board = new Board(canvas);
    this.player = new Player(this.board);
    this.questionUI = new QuestionUI();
    this.ai = new AIEngine();
    this.sound = new SoundManager();

    this.tileQuestions = {};
    this.usedQuestionIds = [];
    this.stageUsedQuestionIds = [];

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

    this.stageNameEl = document.getElementById("stageName");
    this.playerGreetingEl = document.getElementById("playerGreeting");
    this.headerAvatarEl = document.getElementById("headerAvatar");

    this.resultOverlay = document.getElementById("resultOverlay");
    this.resultCard = document.getElementById("resultCard");
    this.resultEmoji = document.getElementById("resultEmoji");
    this.resultTitle = document.getElementById("resultTitle");
    this.resultMessage = document.getElementById("resultMessage");
    this.closeResultBtn = document.getElementById("closeResultBtn");

    this.isRolling = false;

    if (this.closeResultBtn) {
      this.closeResultBtn.onclick = () => this.hideResult();
    }

    if (this.continueBtn) {
      this.continueBtn.onclick = () => this.startNextStage();
    }

    if (this.newGameBtn) {
      this.newGameBtn.onclick = () => this.restartFullGame();
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

  setProfile(name, avatar) {
    this.playerName = (name || "Người chơi").trim();
    this.avatar = avatar || "🐝";

    if (this.headerAvatarEl) {
      this.headerAvatarEl.innerText = this.avatar;
    }

    this.saveState();
    this.updateHUD();
  }

  getStageName(stage) {
    if (stage <= 2) return "Khởi động";
    if (stage <= 4) return "Tăng tốc";
    if (stage <= 6) return "Tự tin";
    if (stage <= 9) return "Vượt thử thách";
    if (stage <= 12) return "Bứt phá";
    if (stage <= 15) return "Chuyên gia nhí";
    return "Siêu ong học tập";
  }

  async rollDice() {
    if (this.isRolling) return;
    if (this.player.position >= this.maxTile) return;

    this.isRolling = true;

    if (this.rollButton) {
      this.rollButton.disabled = true;
    }

    if (this.continueBtn) {
      this.continueBtn.classList.add("hidden");
    }

    this.setStatus("🎲 Đang tung xúc xắc...");
    this.sound.playDice();

    const displayDice = Math.floor(Math.random() * 6) + 1;
    await this.animateDice(displayDice);

    const nextTile = Math.min(this.player.position + 1, this.maxTile);
    this.setStatus(`🐝 Ong đang bay đến ô số ${nextTile}...`);

    await this.animatePlayerSteps(1);

    this.updateHUD();
    await this.triggerQuestion();
  }

  animateDice(finalValue) {
    return new Promise((resolve) => {
      let frame = 0;
      const totalFrames = 12;

      const tick = () => {
        frame += 1;

        if (this.diceResultEl) {
          const tempValue = Math.floor(Math.random() * 6) + 1;
          this.diceResultEl.innerText = `🎲 ${tempValue}`;
        }

        if (frame < totalFrames) {
          setTimeout(tick, 55);
        } else {
          if (this.diceResultEl) {
            this.diceResultEl.innerText = `🎲 ${finalValue}`;
          }
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

      await this.player.animateToTile(targetTile, 320);
      this.render();
      this.updateHUD();
    }
  }

  async fetchQuestionWithFallback(subject, difficulty) {
    const levels = [difficulty, "medium", "easy", "hard"].filter(
      (value, index, arr) => arr.indexOf(value) === index
    );

    const mergedExcludedIds = [
      ...new Set([...this.usedQuestionIds, ...this.stageUsedQuestionIds])
    ];

    for (const level of levels) {
      try {
        const question = await getQuestion(subject, level, mergedExcludedIds);
        return {
          ...question,
          difficulty: level
        };
      } catch (error) {
        console.warn(`Không lấy được câu ${subject}/${level}`, error);
      }
    }

    for (const level of levels) {
      try {
        const question = await getQuestion(subject, level, this.stageUsedQuestionIds);
        return {
          ...question,
          difficulty: level
        };
      } catch (error) {
        console.warn(`Fallback fail ${subject}/${level}`, error);
      }
    }

    for (const level of levels) {
      try {
        const question = await getQuestion(subject, level, []);
        return {
          ...question,
          difficulty: level
        };
      } catch (error) {
        console.warn(`Final fallback fail ${subject}/${level}`, error);
      }
    }

    throw new Error("Không tải được câu hỏi");
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
        question = await this.fetchQuestionWithFallback(subject, difficulty);
        this.tileQuestions[tile] = question;
      }

      this.questionUI.show(
        {
          subject,
          difficulty: question.difficulty || difficulty,
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
      this.setStatus("Không tải được câu hỏi. Kiểm tra backend hoặc dữ liệu.");
      this.questionUI.clear();
      this.isRolling = false;

      if (this.rollButton) {
        this.rollButton.disabled = false;
      }
    }
  }

  handleAnswer(correct) {
    this.ai.recordResult(correct);

    const tile = this.player.position;
    const currentQuestion = this.tileQuestions[tile];

    if (correct) {
      if (currentQuestion) {
        if (!this.usedQuestionIds.includes(currentQuestion.id)) {
          this.usedQuestionIds.push(currentQuestion.id);
        }

        if (!this.stageUsedQuestionIds.includes(currentQuestion.id)) {
          this.stageUsedQuestionIds.push(currentQuestion.id);
        }
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

        if (this.rollButton) {
          this.rollButton.disabled = true;
        }

        this.isRolling = false;
      } else {
        this.isRolling = false;
        if (this.rollButton) {
          this.rollButton.disabled = false;
        }
      }
    } else {
      this.revives -= 1;
      this.sound.playWrong();

      if (this.revives > 0) {
        this.setStatus(`❌ Sai rồi. Em còn ${this.revives} lượt hồi sinh.`);
        this.showLoseResult(false);
        this.isRolling = false;

        if (this.rollButton) {
          this.rollButton.disabled = false;
        }
      } else {
        this.setStatus(`💥 Hết lượt hồi sinh. Quay lại đầu màn ${this.currentStage}!`);
        this.player.reset();
        this.revives = this.maxRevives;
        this.tileQuestions = {};
        this.stageUsedQuestionIds = [];
        this.questionUI.clear();
        this.showLoseResult(true);
        this.isRolling = false;

        if (this.rollButton) {
          this.rollButton.disabled = false;
        }
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
      `Rất tốt ${this.playerName}! Đã hoàn thành đủ 20 câu và nhận thêm ${this.stageReward} điểm thưởng.`;

    if (this.closeResultBtn) {
      this.closeResultBtn.innerText = "Đóng";
    }

    this.resultOverlay.classList.remove("hidden");
  }

  showLoseResult(isResetToStart) {
    if (!this.resultOverlay) return;

    this.resultCard.className = "result-card lose";
    this.resultEmoji.innerText = isResetToStart ? "💥" : "😵";
    this.resultTitle.innerText = isResetToStart ? "Hết lượt hồi sinh" : "Trả lời sai";
    this.resultMessage.innerText = isResetToStart
      ? `Quay lại ô số 1 của màn ${this.currentStage}. Tiếp tục cố gắng nhé!`
      : "Không sao, vẫn còn cơ hội để tiếp tục.";

    if (this.closeResultBtn) {
      this.closeResultBtn.innerText = "Tiếp tục";
      this.closeResultBtn.onclick = () => this.hideResult();
    }

    this.resultOverlay.classList.remove("hidden");
  }

  startNextStage() {
    this.hideResult();

    this.currentStage += 1;
    this.player.reset();
    this.revives = this.maxRevives;
    this.tileQuestions = {};
    this.stageUsedQuestionIds = [];
    this.isRolling = false;

    if (this.rollButton) {
      this.rollButton.disabled = false;
    }

    if (this.continueBtn) {
      this.continueBtn.classList.add("hidden");
    }

    this.questionUI.clear();
    this.setStatus(`🚀 Bắt đầu màn ${this.currentStage}! Mỗi ô là một câu hỏi.`);
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
    this.stageUsedQuestionIds = [];
    this.player.reset();
    this.questionUI.clear();

    this.isRolling = false;

    if (this.rollButton) {
      this.rollButton.disabled = false;
    }

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
      usedQuestionIds: this.usedQuestionIds,
      stageUsedQuestionIds: this.stageUsedQuestionIds,
      playerName: this.playerName,
      avatar: this.avatar
    });
  }

  loadState() {
    const data = loadGame();
    if (!data) return;

    this.currentStage = data.currentStage || 1;
    this.player.position = data.position || 1;
    this.revives = data.revives || this.maxRevives;
    this.score = data.score || 0;
    this.tileQuestions = data.questions || {};
    this.usedQuestionIds = data.usedQuestionIds || [];
    this.stageUsedQuestionIds = data.stageUsedQuestionIds || [];
    this.playerName = data.playerName || "Người chơi";
    this.avatar = data.avatar || "🐝";
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

    if (this.stageNameEl) {
      this.stageNameEl.innerText = this.getStageName(this.currentStage);
    }

    if (this.playerGreetingEl) {
      this.playerGreetingEl.innerText = `Chào mừng ${this.playerName} đến với trò chơi!`;
    }

    if (this.headerAvatarEl) {
      this.headerAvatarEl.innerText = this.avatar;
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