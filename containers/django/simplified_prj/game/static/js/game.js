//==============================================================================
// RUNNER
//==============================================================================

class GameRunner {
  constructor(id, game, cfg) {
    // Assigner les paramètres de configuration avec les valeurs par défaut
    this.cfg = Object.assign({}, game.Defaults || {}, cfg || {});
    this.fps = this.cfg.fps || 60;
    this.interval = 1000.0 / this.fps;

    // Obtenir le canvas et configurer ses dimensions
    this.canvas = document.getElementById(id);
    if (!this.canvas) {
      throw new Error(`Canvas with id ${id} not found`);
    }
    this.width = this.cfg.width || this.canvas.offsetWidth;
    this.height = this.cfg.height || this.canvas.offsetHeight;
    this.front = this.canvas;
    this.front.width = this.width;
    this.front.height = this.height;

    // Créer un canvas arrière pour le double buffering
    this.back = Game.createCanvas();
    this.back.width = this.width;
    this.back.height = this.height;
    this.front2d = this.front.getContext('2d');
    this.back2d = this.back.getContext('2d');
    
    this.addEvents();

    // Initialiser le jeu
    this.game = new game(this, this.cfg);
  }

  start() {
    this.lastFrame = Game.timestamp();
    this.timer = setInterval(this.loop.bind(this), this.interval);
  }

  stop() {
    clearInterval(this.timer);
  }

  loop() {
    const start = Game.timestamp();
    this.update((start - this.lastFrame) / 1000.0);
    this.draw();
    this.lastFrame = start;
  }

  update(dt) {
    this.game.update(dt);
  }

  draw() {
    // Effacer le canvas arrière et dessiner le contenu du jeu
    this.back2d.clearRect(0, 0, this.width, this.height);
    this.game.draw(this.back2d);
    
    // Effacer le canvas avant et copier le contenu du canvas arrière
    this.front2d.clearRect(0, 0, this.width, this.height);
    this.front2d.drawImage(this.back, 0, 0);
  }

  addEvents() {
    Game.addEvent(document, 'keydown', this.onkeydown.bind(this));
    Game.addEvent(document, 'keyup', this.onkeyup.bind(this));
    if (this.cfg.multi)
      Game.addEvent(this.cfg.socket, 'message', this.onSocketMessage.bind(this))
    Game.addEvent(window, 'blur', this.onWindowBlur.bind(this));
    Game.addEvent(window, 'focus', this.onWindowFocus.bind(this));
  }

  onkeydown(ev) { if (this.game.onkeydown) this.game.onkeydown(ev.keyCode); }
  onkeyup(ev) { if (this.game.onkeyup) this.game.onkeyup(ev.keyCode); }

  onSocketMessage(ev) {
    const data = JSON.parse(ev.data);

    if (data['type'] === 'game_state_update') {
      let ball_x = data['state']['ball_position_x'];
      if (data['state']['initiator_id'] === this.cfg.me.id ) {
        this.game.opponentPaddle.setpos(this.game.opponentPaddle.x, data['state']['invited_paddle_y']);
        this.game.ball.setpos(ball_x, data['state']['ball_position_y']);
        this.game.setScore(data['state']['initiator_score'], data['state']['invited_score']);
      } else {
        this.game.opponentPaddle.setpos(this.game.opponentPaddle.x, data['state']['initiator_paddle_y']);
        this.game.ball.setpos(this.cfg.width - ball_x, data['state']['ball_position_y']);
        this.game.setScore(data['state']['invited_score'], data['state']['initiator_score']);
      }
      this.game.ball.setdir(data['state']['ball_direction_x'], data['state']['ball_direction_y']);
      if (data['state']['tournament'] == true) {
        this.game.tournament = true;
        this.game.timerMin = data['state']['minutes_left'];
        this.game.timerSec = data['state']['seconds_left'];
      }
    }
    if (data['type'] === 'game_ended')
    {
      if (data['initiator_id'] === this.cfg.me.id ) {
        this.game.setScore(data['initiator_score'], data['invited_score']);
      } else {
        this.game.setScore(data['invited_score'], data['initiator_score']);
      }
      this.game.stop();
    }
  }

  onWindowBlur() { if (this.game.onWindowBlur) this.game.onWindowBlur(); }
  onWindowFocus() { if (this.game.onWindowFocus) this.game.onWindowFocus(); }

  hideCursor() { this.canvas.style.cursor = 'none'; }
  showCursor() { this.canvas.style.cursor = 'auto'; }

  confirm(msg) {
    this.stop();
    let result = window.confirm(msg);
    this.start();
    return result;
  }
}

//==============================================================================
// GAME
//==============================================================================

const Game = {
  addEvent(obj, type, fn) {
    obj.addEventListener(type, fn, false);
  },

  removeEvent(obj, type, fn) {
    obj.removeEventListener(type, fn, false); 
  },
  
  ready(fn) {
    Game.addEvent(document, 'DOMContentLoaded', fn);
  },
  
  start(id, game, cfg) {
    return new GameRunner(id, game, cfg).game;
  },
  
  createCanvas() {
    return document.createElement('canvas');
  },
  
  random(min, max) {
    return min + (Math.random() * (max - min));
  },
  
  timestamp() {
    return new Date().getTime();
  },
  
  KEY: {
    RETURN: 13,
    ESC: 27,
    A: 65,
    L: 76,
    P: 80,
    Q: 81
  }
};
