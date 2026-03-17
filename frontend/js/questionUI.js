export default class QuestionUI {
  constructor() {
    this.badge = document.getElementById("questionBadge");
    this.title = document.getElementById("questionTitle");
    this.text = document.getElementById("questionText");
    this.answers = document.getElementById("answers");
  }

  showLoading() {
    if (this.badge) {
      this.badge.innerText = "Đang tải câu hỏi";
      this.badge.className = "question-badge neutral";
    }

    if (this.title) {
      this.title.innerText = "Chuẩn bị câu hỏi";
    }

    if (this.text) {
      this.text.innerText = "Vui lòng chờ một chút...";
    }

    if (this.answers) {
      this.answers.innerHTML = "";

      const btn = document.createElement("button");
      btn.className = "answer-btn answer-btn-loading";
      btn.disabled = true;
      btn.innerHTML = `
        <span class="answer-letter">…</span>
        <span class="answer-content">Đang lấy dữ liệu...</span>
      `;

      this.answers.appendChild(btn);
    }
  }

  show(question, onAnswered) {
    const subjectLabel = this.formatSubject(question.subject);
    const difficultyLabel = this.formatDifficulty(question.difficulty);

    if (this.badge) {
      this.badge.innerText = `${subjectLabel} • ${difficultyLabel}`;
      this.badge.className = `question-badge ${question.subject}`;
    }

    if (this.title) {
      this.title.innerText = "Trả lời câu hỏi";
    }

    if (this.text) {
      this.text.innerText = question.text;
    }

    if (!this.answers) return;

    this.answers.innerHTML = "";
    let locked = false;

    question.options.forEach((opt, index) => {
      const btn = document.createElement("button");
      btn.className = "answer-btn";

      btn.innerHTML = `
        <span class="answer-letter">${String.fromCharCode(65 + index)}</span>
        <span class="answer-content">${opt}</span>
      `;

      btn.onclick = () => {
        if (locked) return;
        locked = true;

        const isCorrect = opt === question.answer;
        const allButtons = this.answers.querySelectorAll(".answer-btn");

        allButtons.forEach((item) => {
          item.disabled = true;
          item.classList.add("is-locked");
        });

        if (isCorrect) {
          btn.classList.add("is-correct");
        } else {
          btn.classList.add("is-wrong");

          allButtons.forEach((item) => {
            const content = item.querySelector(".answer-content");
            if (content && content.textContent === question.answer) {
              item.classList.add("is-correct");
            }
          });
        }

        setTimeout(() => {
          if (typeof onAnswered === "function") {
            onAnswered(isCorrect);
          }
        }, 650);
      };

      this.answers.appendChild(btn);
    });
  }

  clear() {
    if (this.badge) {
      this.badge.innerText = "Chưa có câu hỏi";
      this.badge.className = "question-badge neutral";
    }

    if (this.title) {
      this.title.innerText = "Câu hỏi sẽ hiển thị ở đây";
    }

    if (this.text) {
      this.text.innerText = "Nhấn “Đi tiếp” để di chuyển đến ô mới và nhận câu hỏi.";
    }

    if (this.answers) {
      this.answers.innerHTML = "";
    }
  }

  formatSubject(subject) {
    if (subject === "math") return "Toán";
    if (subject === "english") return "Tiếng Anh";
    return "Tiếng Việt";
  }

  formatDifficulty(difficulty) {
    if (difficulty === "easy") return "Dễ";
    if (difficulty === "medium") return "Trung bình";
    return "Khó";
  }
}