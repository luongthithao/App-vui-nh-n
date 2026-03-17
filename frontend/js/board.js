export default class Board {
  constructor(canvas) {
    this.canvas = canvas;
    this.ctx = canvas.getContext("2d");

    this.rows = 4;
    this.cols = 5;

    this.tileSize = 90;
    this.gapX = 34;
    this.gapY = 34;

    this.tiles = [];
    this.generateTiles();
  }

  generateTiles() {
    this.tiles = [];

    const boardWidth =
      this.cols * this.tileSize + (this.cols - 1) * this.gapX;

    const boardHeight =
      this.rows * this.tileSize + (this.rows - 1) * this.gapY;

    const startX = (this.canvas.width - boardWidth) / 2;
    const startY = (this.canvas.height - boardHeight) / 2 + 26;

    let number = 1;

    for (let row = 0; row < this.rows; row++) {
      const reverse = row % 2 === 1;

      for (let col = 0; col < this.cols; col++) {
        const visualCol = reverse ? this.cols - 1 - col : col;

        const baseX = startX + visualCol * (this.tileSize + this.gapX);
        const baseY = startY + (this.rows - 1 - row) * (this.tileSize + this.gapY);

        const offsetX = Math.sin((row + visualCol) * 0.8) * 8;
        const offsetY = Math.cos(visualCol * 0.9 + row * 0.7) * 16;

        const x = baseX + offsetX;
        const y = baseY + offsetY;

        this.tiles.push({ number, x, y });
        number++;
      }
    }
  }

  getTileType(number) {
    if (number === 1) return "start";
    if (number === 20) return "finish";
    if ([2, 5, 8, 10, 12, 15, 18].includes(number)) return "math";
    if ([3, 6, 9, 13, 16, 19].includes(number)) return "english";
    return "vietnamese";
  }

  getTileColor(type) {
    if (type === "start") return "#22c55e";
    if (type === "finish") return "#16a34a";
    if (type === "math") return "#facc15";
    if (type === "english") return "#38bdf8";
    return "#c084fc";
  }

  shadeColor(hex, percent) {
    const num = parseInt(hex.replace("#", ""), 16);

    let r = (num >> 16) + percent;
    let g = ((num >> 8) & 0x00ff) + percent;
    let b = (num & 0x0000ff) + percent;

    r = Math.max(0, Math.min(255, r));
    g = Math.max(0, Math.min(255, g));
    b = Math.max(0, Math.min(255, b));

    return `rgb(${r}, ${g}, ${b})`;
  }

  drawCloud(x, y, scale = 1) {
    const ctx = this.ctx;

    ctx.save();
    ctx.translate(x, y);
    ctx.scale(scale, scale);

    ctx.fillStyle = "rgba(255,255,255,0.72)";
    ctx.beginPath();
    ctx.arc(0, 0, 18, 0, Math.PI * 2);
    ctx.arc(20, -8, 24, 0, Math.PI * 2);
    ctx.arc(48, 0, 18, 0, Math.PI * 2);
    ctx.arc(24, 10, 22, 0, Math.PI * 2);
    ctx.fill();

    ctx.restore();
  }

  drawBackground() {
    const spacing = this.canvas.width / 6;

    for (let i = 0; i < 6; i++) {
      this.drawCloud(110 + i * spacing, 92 + (i % 2) * 10, 0.9);
    }
  }

  drawPath() {
    const ctx = this.ctx;

    const points = this.tiles.map((tile) => ({
      x: tile.x + this.tileSize / 2,
      y: tile.y + this.tileSize / 2
    }));

    ctx.save();
    ctx.strokeStyle = "rgba(255,255,255,0.44)";
    ctx.lineWidth = 16;
    ctx.lineCap = "round";
    ctx.lineJoin = "round";

    ctx.beginPath();

    points.forEach((point, index) => {
      if (index === 0) {
        ctx.moveTo(point.x, point.y);
        return;
      }

      const prev = points[index - 1];
      const midX = (prev.x + point.x) / 2;
      const midY = (prev.y + point.y) / 2;

      ctx.quadraticCurveTo(prev.x, prev.y, midX, midY);

      if (index === points.length - 1) {
        ctx.quadraticCurveTo(midX, midY, point.x, point.y);
      }
    });

    ctx.stroke();

    ctx.strokeStyle = "rgba(255,255,255,0.16)";
    ctx.lineWidth = 6;
    ctx.stroke();

    ctx.restore();
  }

  drawSingleTile(tile, isActive) {
    const ctx = this.ctx;
    const type = this.getTileType(tile.number);
    const color = this.getTileColor(type);

    ctx.save();

    ctx.beginPath();
    ctx.roundRect(tile.x, tile.y, this.tileSize, this.tileSize, 22);

    const gradient = ctx.createLinearGradient(
      tile.x,
      tile.y,
      tile.x,
      tile.y + this.tileSize
    );
    gradient.addColorStop(0, "#ffffff");
    gradient.addColorStop(0.06, color);
    gradient.addColorStop(1, this.shadeColor(color, -18));

    ctx.fillStyle = gradient;
    ctx.fill();

    ctx.strokeStyle = isActive ? "#ffffff" : "rgba(17,24,39,0.24)";
    ctx.lineWidth = isActive ? 6 : 3;
    ctx.stroke();

    if (isActive) {
      ctx.shadowColor = "rgba(255,255,255,0.85)";
      ctx.shadowBlur = 18;
      ctx.stroke();
      ctx.shadowBlur = 0;
    }

    ctx.fillStyle = "#0f172a";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.font = "bold 34px Arial";
    ctx.fillText(
      String(tile.number),
      tile.x + this.tileSize / 2,
      tile.y + this.tileSize / 2
    );

    if (tile.number === 1) {
      ctx.font = "bold 12px Arial";
      ctx.fillText("START", tile.x + this.tileSize / 2, tile.y + this.tileSize - 14);
    }

    if (tile.number === 20) {
      ctx.font = "bold 12px Arial";
      ctx.fillText("FINISH", tile.x + this.tileSize / 2, tile.y + this.tileSize - 14);
    }

    ctx.restore();
  }

  draw(playerPosition) {
    const ctx = this.ctx;
    ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

    this.drawBackground();
    this.drawPath();

    this.tiles.forEach((tile) => {
      this.drawSingleTile(tile, tile.number === playerPosition);
    });
  }

  getTilePosition(tileNumber) {
    return this.tiles[tileNumber - 1];
  }
}