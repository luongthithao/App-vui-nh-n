export default class QuestionUI {
  constructor() {
    this.badge = document.getElementById("questionBadge");
    this.title = document.getElementById("questionTitle");
    this.text = document.getElementById("questionText");
    this.answers = document.getElementById("answers");
  }

  show(question, onAnswered) {
    const subjectLabel = this.formatSubject(question.subject);
    const difficultyLabel = this.formatDifficulty(question.difficulty);

    this.badge.innerText = `${subjectLabel} • ${difficultyLabel}`;
    this.badge.className = "question-badge";
    this.badge.style.background = this.getBadgeBg(question.subject);
    this.badge.style.color = this.getBadgeColor(question.subject);

    this.title.innerText = "Trả lời câu hỏi";
    this.text.innerText = question.text;
    this.answers.innerHTML = "";

    question.options.forEach((opt, index) => {
      const btn = document.createElement("button");
      btn.className = "answer-btn";
      btn.innerText = `${String.fromCharCode(65 + index)}. ${opt}`;

      btn.onclick = () => {
        const isCorrect = opt === question.answer;

        if (typeof onAnswered === "function") {
          onAnswered(isCorrect);
        }
      };

      this.answers.appendChild(btn);
    });
  }

  clear() {
    this.badge.innerText = "Chưa có câu hỏi";
    this.badge.className = "question-badge neutral";
    this.badge.style.background = "";
    this.badge.style.color = "";

    this.title.innerText = "Câu hỏi sẽ hiển thị ở đây";
    this.text.innerText = "Nhấn “Đi tiếp” để di chuyển đến ô mới và nhận câu hỏi.";
    this.answers.innerHTML = "";
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

  getBadgeBg(subject) {
    if (subject === "math") return "#fef3c7";
    if (subject === "english") return "#dbeafe";
    return "#f3e8ff";
  }

  getBadgeColor(subject) {
    if (subject === "math") return "#b45309";
    if (subject === "english") return "#1d4ed8";
    return "#7c3aed";
  }
}