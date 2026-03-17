export default class Player {
  constructor(board) {
    this.board = board;
    this.position = 1;

    this.image = new Image();
    this.image.src = "assets/bee.png";

    const startTile = this.board.getTilePosition(1);

    this.drawX = startTile.x + this.board.tileSize / 2;
    this.drawY = startTile.y + this.board.tileSize / 2;

    this.size = 46;
    this.bobOffset = 0;
  }

  move(step) {
    this.position += step;

    if (this.position > 20) {
      this.position = 20;
    }
  }

  reset() {
    this.position = 1;

    const tile = this.board.getTilePosition(1);

    this.drawX = tile.x + this.board.tileSize / 2;
    this.drawY = tile.y + this.board.tileSize / 2;
  }

  syncToTile() {
    const tile = this.board.getTilePosition(this.position);

    this.drawX = tile.x + this.board.tileSize / 2;
    this.drawY = tile.y + this.board.tileSize / 2;
  }

  async animateToTile(targetTile, duration = 260) {
    return new Promise((resolve) => {
      const startX = this.drawX;
      const startY = this.drawY;

      const endX = targetTile.x + this.board.tileSize / 2;
      const endY = targetTile.y + this.board.tileSize / 2;

      const startTime = performance.now();

      const animate = (now) => {
        const elapsed = now - startTime;
        const t = Math.min(elapsed / duration, 1);

        const eased = this.easeInOutQuad(t);

        this.drawX = startX + (endX - startX) * eased;
        this.drawY = startY + (endY - startY) * eased;

        if (t < 1) {
          requestAnimationFrame(animate);
        } else {
          this.drawX = endX;
          this.drawY = endY;
          resolve();
        }
      };

      requestAnimationFrame(animate);
    });
  }

  easeInOutQuad(t) {
    return t < 0.5
      ? 2 * t * t
      : 1 - Math.pow(-2 * t + 2, 2) / 2;
  }

  draw(ctx) {
    this.bobOffset += 0.08;

    const bob = Math.sin(this.bobOffset) * 2;

    const x = this.drawX;
    const y = this.drawY + bob;

    ctx.save();

    ctx.shadowColor = "rgba(0,0,0,0.25)";
    ctx.shadowBlur = 10;

    ctx.fillStyle = "rgba(0,0,0,0.18)";
    ctx.beginPath();
    ctx.ellipse(x, y + 20, 16, 8, 0, 0, Math.PI * 2);
    ctx.fill();

    ctx.shadowBlur = 0;

    if (this.image.complete && this.image.naturalWidth > 0) {
      ctx.drawImage(
        this.image,
        x - this.size / 2,
        y - this.size / 2,
        this.size,
        this.size
      );
    } else {
      ctx.fillStyle = "#f59e0b";

      ctx.beginPath();
      ctx.arc(x, y, 16, 0, Math.PI * 2);
      ctx.fill();
    }

    ctx.restore();
  }
}