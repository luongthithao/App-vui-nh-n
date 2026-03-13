export default class Board {
  constructor(canvas) {
    this.canvas = canvas;
    this.ctx = canvas.getContext("2d");

    this.tileSize = 84;
    this.tiles = this.createTiles();
  }

  createTiles() {
    return [
      { number: 1,  x: 120, y: 500 },
      { number: 2,  x: 240, y: 500 },
      { number: 3,  x: 360, y: 500 },
      { number: 4,  x: 480, y: 500 },
      { number: 5,  x: 600, y: 500 },

      { number: 6,  x: 700, y: 420 },
      { number: 7,  x: 580, y: 420 },
      { number: 8,  x: 460, y: 420 },
      { number: 9,  x: 340, y: 420 },
      { number: 10, x: 220, y: 420 },

      { number: 11, x: 120, y: 335 },
      { number: 12, x: 240, y: 335 },
      { number: 13, x: 360, y: 335 },
      { number: 14, x: 480, y: 335 },
      { number: 15, x: 600, y: 335 },

      { number: 16, x: 700, y: 250 },
      { number: 17, x: 580, y: 250 },
      { number: 18, x: 460, y: 250 },
      { number: 19, x: 340, y: 250 },
      { number: 20, x: 220, y: 250 }
    ];
  }

  getTileType(number) {
    if (number === 1) return "start";
    if (number === 20) return "finish";

    if ([2,5,8,10,12,15,18].includes(number)) return "math";
    if ([3,6,9,13,16,19].includes(number)) return "english";
    return "vietnamese";
  }

  getTileColor(type) {
    if (type === "start") return "#22c55e";
    if (type === "finish") return "#16a34a";
    if (type === "math") return "#facc15";
    if (type === "english") return "#38bdf8";
    return "#c084fc";
  }

  getIcon(type) {
    if (type === "math") return "➕";
    if (type === "english") return "EN";
    if (type === "vietnamese") return "TV";
    if (type === "start") return "▶";
    if (type === "finish") return "🏁";
    return "";
  }

  drawBackground() {
    const ctx = this.ctx;

    ctx.save();

    for (let i = 0; i < 6; i++) {
      const x = 80 + i * 150;
      const y = 80 + (i % 2) * 22;
      this.drawCloud(x, y, 0.8);
    }

    ctx.restore();
  }

  drawCloud(x, y, scale = 1) {
    const ctx = this.ctx;
    ctx.save();
    ctx.translate(x, y);
    ctx.scale(scale, scale);

    ctx.fillStyle = "rgba(255,255,255,0.75)";
    ctx.beginPath();
    ctx.arc(0, 0, 18, 0, Math.PI * 2);
    ctx.arc(20, -8, 24, 0, Math.PI * 2);
    ctx.arc(48, 0, 18, 0, Math.PI * 2);
    ctx.arc(24, 10, 22, 0, Math.PI * 2);
    ctx.fill();

    ctx.restore();
  }

  drawPath() {
    const ctx = this.ctx;

    ctx.save();
    ctx.strokeStyle = "rgba(255,255,255,0.55)";
    ctx.lineWidth = 14;
    ctx.lineCap = "round";
    ctx.lineJoin = "round";

    ctx.beginPath();

    this.tiles.forEach((tile, index) => {
      const cx = tile.x + this.tileSize / 2;
      const cy = tile.y + this.tileSize / 2;

      if (index === 0) ctx.moveTo(cx, cy);
      else ctx.lineTo(cx, cy);
    });

    ctx.stroke();

    ctx.strokeStyle = "rgba(255,255,255,0.2)";
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

    const gradient = ctx.createLinearGradient(tile.x, tile.y, tile.x, tile.y + this.tileSize);
    gradient.addColorStop(0, "#ffffff");
    gradient.addColorStop(0.05, color);
    gradient.addColorStop(1, this.shadeColor(color, -18));

    ctx.fillStyle = gradient;
    ctx.fill();

    ctx.strokeStyle = isActive ? "#ffffff" : "rgba(17,24,39,0.32)";
    ctx.lineWidth = isActive ? 6 : 3;
    ctx.stroke();

    if (isActive) {
      ctx.shadowColor = "rgba(255,255,255,0.8)";
      ctx.shadowBlur = 18;
      ctx.stroke();
      ctx.shadowBlur = 0;
    }

    ctx.fillStyle = "#0f172a";
    ctx.font = "bold 15px Arial";
    ctx.textAlign = "center";
    ctx.fillText(this.getIcon(type), tile.x + this.tileSize / 2, tile.y + 22);

    ctx.font = "bold 22px Arial";
    ctx.fillText(String(tile.number), tile.x + this.tileSize / 2, tile.y + 54);

    if (tile.number === 1) {
      ctx.font = "bold 12px Arial";
      ctx.fillText("START", tile.x + this.tileSize / 2, tile.y + 73);
    }

    if (tile.number === 20) {
      ctx.font = "bold 12px Arial";
      ctx.fillText("FINISH", tile.x + this.tileSize / 2, tile.y + 73);
    }

    ctx.restore();
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

  draw(playerPosition) {
    const ctx = this.ctx;
    ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

    this.drawBackground();
    this.drawPath();

    this.tiles.forEach(tile => {
      this.drawSingleTile(tile, tile.number === playerPosition);
    });
  }

  getTilePosition(tileNumber) {
    return this.tiles[tileNumber - 1];
  }
}