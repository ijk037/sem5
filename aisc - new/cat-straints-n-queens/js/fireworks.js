/**
 * Cute Fireworks & Confetti Celebration Engine
 */
class FireworksEngine {
  constructor() {
    this.canvas = null;
    this.ctx = null;
    this.particles = [];
    this.rockets = [];
    this.isRunning = false;
    this.animId = null;
    this.colors = [
      '#ff7675', '#fd79a8', '#a29bfe', '#6c5ce7',
      '#ffeaa7', '#fdcb6e', '#55efc4', '#00b894',
      '#74b9ff', '#0984e3', '#fab1a0', '#ff9ff3'
    ];
  }

  init(canvasElement) {
    this.canvas = canvasElement;
    this.ctx = this.canvas.getContext('2d');
    this.resize();
    window.addEventListener('resize', () => this.resize());
  }

  resize() {
    if (!this.canvas) return;
    this.canvas.width = window.innerWidth;
    this.canvas.height = window.innerHeight;
  }

  launch(durationMs = 4500) {
    if (!this.canvas) return;
    this.resize();
    this.particles = [];
    this.rockets = [];
    this.isRunning = true;

    // Launch multiple rockets over time
    const startTime = Date.now();
    const interval = setInterval(() => {
      if (Date.now() - startTime > durationMs) {
        clearInterval(interval);
        return;
      }
      this.createRocket();
      if (Math.random() > 0.4) {
        setTimeout(() => this.createRocket(), 150);
      }
    }, 280);

    // Initial burst immediately
    for (let i = 0; i < 3; i++) {
      this.createRocket(window.innerWidth * (0.25 + i * 0.25));
    }

    if (!this.animId) {
      this.loop();
    }
  }

  createRocket(startX) {
    const x = startX !== undefined ? startX : Math.random() * (this.canvas.width * 0.8) + (this.canvas.width * 0.1);
    const targetY = Math.random() * (this.canvas.height * 0.45) + (this.canvas.height * 0.12);
    const color = this.colors[Math.floor(Math.random() * this.colors.length)];

    this.rockets.push({
      x,
      y: this.canvas.height + 10,
      targetY,
      color,
      speed: 12 + Math.random() * 5,
      trail: []
    });
  }

  explode(x, y, baseColor) {
    const particleCount = 45 + Math.floor(Math.random() * 25);
    const isPawShape = Math.random() > 0.6;

    for (let i = 0; i < particleCount; i++) {
      const angle = (Math.PI * 2 / particleCount) * i + (Math.random() * 0.2);
      const speed = Math.random() * 6 + 2;
      const color = Math.random() > 0.3 ? baseColor : this.colors[Math.floor(Math.random() * this.colors.length)];

      this.particles.push({
        x,
        y,
        vx: Math.cos(angle) * speed,
        vy: Math.sin(angle) * speed,
        alpha: 1,
        color,
        size: Math.random() * 4 + 2.5,
        drag: 0.94,
        gravity: 0.12,
        wobble: Math.random() * 10,
        shape: isPawShape && i % 3 === 0 ? 'star' : 'circle'
      });
    }

    // Also spawn some floating confetti ribbons
    for (let j = 0; j < 12; j++) {
      const angle = Math.random() * Math.PI * 2;
      const speed = Math.random() * 4 + 1.5;
      this.particles.push({
        x,
        y,
        vx: Math.cos(angle) * speed,
        vy: Math.sin(angle) * speed,
        alpha: 1,
        color: this.colors[Math.floor(Math.random() * this.colors.length)],
        size: Math.random() * 7 + 4,
        drag: 0.95,
        gravity: 0.08,
        wobble: Math.random() * Math.PI * 2,
        wobbleSpeed: 0.08 + Math.random() * 0.05,
        shape: 'confetti'
      });
    }
  }

  loop() {
    if (!this.isRunning) {
      this.animId = null;
      return;
    }

    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

    // Update rockets
    for (let i = this.rockets.length - 1; i >= 0; i--) {
      const r = this.rockets[i];
      r.y -= r.speed;

      // Draw rocket trail
      this.ctx.beginPath();
      this.ctx.arc(r.x, r.y, 3, 0, Math.PI * 2);
      this.ctx.fillStyle = '#fff';
      this.ctx.shadowBlur = 8;
      this.ctx.shadowColor = r.color;
      this.ctx.fill();
      this.ctx.shadowBlur = 0;

      if (r.y <= r.targetY) {
        this.explode(r.x, r.y, r.color);
        this.rockets.splice(i, 1);
      }
    }

    // Update particles
    for (let i = this.particles.length - 1; i >= 0; i--) {
      const p = this.particles[i];
      p.x += p.vx;
      p.y += p.vy;
      p.vx *= p.drag;
      p.vy *= p.drag;
      p.vy += p.gravity;
      p.alpha -= 0.013;

      if (p.alpha <= 0) {
        this.particles.splice(i, 1);
        continue;
      }

      this.ctx.save();
      this.ctx.globalAlpha = Math.max(0, p.alpha);
      this.ctx.fillStyle = p.color;

      if (p.shape === 'confetti') {
        p.wobble += p.wobbleSpeed;
        const width = p.size;
        const height = p.size * Math.sin(p.wobble);
        this.ctx.translate(p.x, p.y);
        this.ctx.fillRect(-width / 2, -height / 2, width, height);
      } else if (p.shape === 'star') {
        this.ctx.translate(p.x, p.y);
        this.ctx.beginPath();
        for (let s = 0; s < 5; s++) {
          this.ctx.lineTo(Math.cos((18 + s * 72) * 0.0174) * p.size, -Math.sin((18 + s * 72) * 0.0174) * p.size);
          this.ctx.lineTo(Math.cos((54 + s * 72) * 0.0174) * (p.size / 2), -Math.sin((54 + s * 72) * 0.0174) * (p.size / 2));
        }
        this.ctx.closePath();
        this.ctx.fill();
      } else {
        this.ctx.beginPath();
        this.ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
        this.ctx.fill();
      }

      this.ctx.restore();
    }

    if (this.rockets.length === 0 && this.particles.length === 0) {
      this.isRunning = false;
      this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
      this.animId = null;
      return;
    }

    this.animId = requestAnimationFrame(() => this.loop());
  }

  stop() {
    this.isRunning = false;
    this.rockets = [];
    this.particles = [];
    if (this.ctx && this.canvas) {
      this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    }
  }
}

if (typeof window !== 'undefined') {
  window.fireworks = new FireworksEngine();
}
if (typeof module !== 'undefined' && module.exports) {
  module.exports = FireworksEngine;
}
