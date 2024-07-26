//==============================================================================
// PONG
//==============================================================================

class Pong {
    static Defaults = {
    width:        640,
    height:       480,
    wallWidth:    12,
    paddleWidth:  12,
    paddleHeight: 60,
    paddleSpeed:  1,
    ballVelocity:    200,
    ballVelocityIncrease:   10,
    ballRadius:   5
  };
  
  static Colors = {
    walls:           'white',
    ball:            'white',
    score:           'white',
  };
  
//------------------------------------------------------------------------------
  
  constructor(runner, cfg) {
      this.cfg              = cfg;
      this.runner           = runner;
      this.width            = runner.width;
      this.height           = runner.height;
      this.playing          = false;
      this.countingDown     = false;
      this.scores           = [0, 0];
      this.court            = new Pong.Court(this);
      this.myPaddle         = new Pong.Paddle(this, false);
      this.opponentPaddle   = new Pong.Paddle(this, true);
      this.ball             = new Pong.Ball(this);
      this.alpha            = 1.0;
      this.fadeDirection    = -1;
      this.amIReady         = false;
      this.gameStarted      = false;
      this.tournament       = false;
      this.timerMin;
      this.timerSec;
      this.runner.start();
  }

  startCountdown(callback) {
    this.countingDown = true;
    this.countdown = 3;
    this.countdownInterval = setInterval(() => {
      if (this.countdown > 0) {
        this.countdownText = this.countdown;
        this.countdown--;
      } else {
        this.countdownText = "GO!";
        clearInterval(this.countdownInterval);
        setTimeout(() => {
          this.countdownText = "";
          this.countingDown = false;
          callback();
        }, 500); // Delay avant de commencer le jeu
      }
    }, 500); // Intervalle de 1 seconde
  }

  startSinglePlayer() {
    if (!this.playing) {
      this.amIReady = true;
      this.playing = true;
      this.scores = [0,0];
      this.gameStarted = true;
      this.ball.reset();
      this.runner.hideCursor();
    }
  }
  
  startDoublePlayer() {
    if (!this.playing) {
      this.amIReady = true;
      this.cfg.socket.send(JSON.stringify({
        'type':'report_ready'
      }));
      this.cfg.socket.onmessage = (ev) => {
        const data = JSON.parse(ev.data);
        if (data['type'] === 'game_starts') {
          this.startCountdown(() => {
            this.playing = true;
            this.scores = [0, 0];
            this.gameStarted = true;
            this.runner.hideCursor();
          });
        }
      };
    }
  }
  
  stop(ask) {
    if (this.playing) {
      if (!ask || this.runner.confirm('Abandon game in progress ?')) {
        this.playing = false;
        this.runner.showCursor();
        if (this.cfg.mutli && ask)
          this.cfg.socket.send(JSON.stringify({
            'type': 'report_left'
          }));
      }
    }
  }

  setScore(player1_score, player2_score) {
    this.scores = [player1_score, player2_score];
  }

  goal(playerNo) {
    this.scores[playerNo] += 1;
    if (this.scores[playerNo] == 5)
      this.stop();
    else {
      this.ball.reset();
    }
  }
  
  update(dt) {
    if (this.cfg.multi) {
      if (this.playing) {
        const distance = this.myPaddle.update(dt);
        if (distance !== 0) {
          this.cfg.socket.send(JSON.stringify({
            'type': 'paddle_position_update',
            'position': this.myPaddle.y
          }));
        }
      }
    }
    else {
      this.myPaddle.update(dt);
      this.opponentPaddle.update(dt);

      if (this.playing) {
        this.ball.update(dt, this.myPaddle, this.opponentPaddle);

        if (this.ball.left > (this.width - this.cfg.paddleWidth))
          this.goal(0);
        else if (this.ball.right < this.cfg.paddleWidth)
          this.goal(1);
      }
    }
  }

  drawText(ctx, text) {
    ctx.font = '48px Arial';
    ctx.fillStyle = 'white';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(text, this.width / 2, this.height / 2);
  }
  
  fadeOut(ctx, text) {
    ctx.fillStyle = "rgba(255, 255, 255, " + this.alpha + ")";
    ctx.font = "italic 42px Arial";
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(text, this.width / 2, this.height / 2);
    this.alpha += this.fadeDirection * 0.01;
    if (this.alpha <= 0.25 || this.alpha >= 1) {
      this.fadeDirection *= -1;
    }
  }

  displayWinner(ctx, playerNo) {
    ctx.fillStyle = "rgba(255, 255, 255, " + this.alpha + ")";
    ctx.font = "italic 21px Arial";
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';

    if (playerNo == 0) {
      this.textX = this.width / 4;
      this.textY = this.height / 10;
      if (this.scores[playerNo] == 5)
        this.text = "Congrats, you won !";
      else
        this.text = "Game Over!";
      this.alpha += this.fadeDirection * 0.01;
      if (this.alpha <= 0.25 || this.alpha >= 1) {
        this.fadeDirection *= -1;
      }
    }
    else if (playerNo == 1) {
      this.textX = this.width - this.width / 4;
      this.textY = this.height / 10;
      if (this.scores[playerNo] == 5)
        this.text = "Congrats, you won !";
      else
        this.text = "Game Over!";
    }
    ctx.fillText(this.text, this.textX, this.textY);
    ctx.fillText("Press ENTER to play again", this.textX, this.height / 2);
  }

  displayTimer(ctx, minute, second) {
    if (minute > 0 && second > 0) {
      ctx.fillStyle = "white";
      ctx.font = "italic 21px Arial";
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      this.textX = this.width - this.width / 5;
      this.textY = this.height / 10;
      ctx.fillText("Time left to finish:", this.textX, this.textY);
      let formattedSecond = second < 10 ? '0' + second : second;
      this.text = minute + ":" + formattedSecond;
      ctx.font = "21px Arial";
      ctx.fillText(this.text, this.textX, this.textY + 20);
    }
  }

  displayCommands(ctx, isMulti)
  {
    ctx.font = 'italic 16px Arial';
    ctx.fillStyle = 'white';
    ctx.textAlign = 'left';
    ctx.textBaseline = 'middle';
    this.textX = this.width / 8;
    this.textY = this.height / 10;
    ctx.fillText("Player 1 :", this.textX, this.textY);
    ctx.fillText("'Q' : move up", this.textX, this.textY + 20);
    ctx.fillText("'A' : move down", this.textX, this.textY + 40);
    if (!isMulti) {
      ctx.textAlign = 'right';
      this.textX = this.width - this.width / 8;
      this.textY = this.height / 10;
      ctx.fillText("Player 2 :", this.textX, this.textY);
      ctx.fillText("'P' : move up", this.textX, this.textY + 20);
      ctx.fillText("'L' : move down", this.textX, this.textY + 40);
    }
  }

  draw(ctx) {
    if (this.playing) {
      this.court.draw(ctx, this.scores[0], this.scores[1]);
      this.myPaddle.draw(ctx);
      this.opponentPaddle.draw(ctx);
      this.ball.draw(ctx);
      if (this.tournament == true)
        this.displayTimer(ctx, this.timerMin, this.timerSec)
    }
    else if (this.countdownText)
      this.drawText(ctx, this.countdownText);
    else if (!this.gameStarted) {
      if (!this.amIReady) {
        this.fadeOut(ctx, "Press ENTER to play");
        this.displayCommands(ctx, this.cfg.multi);
      }
      else if (this.cfg.multi)
        this.fadeOut(ctx, "Waiting other player");
    }
    else if (this.scores[0] >= 5 || this.scores[1] >= 5) {
      if (this.cfg.multi == true) {
        if (this.scores[0] >= 5)
          this.fadeOut(ctx, "Congrats, you won !");
        else
          this.fadeOut(ctx, "Game Over!");
      }
      else {
        this.court.draw(ctx, this.scores[0], this.scores[1]);
        this.myPaddle.draw(ctx);
        this.opponentPaddle.draw(ctx);
        this.displayWinner(ctx, 0);
        this.displayWinner(ctx, 1);
      }
    }
    else if (this.gameStarted)
      this.fadeOut(ctx, "Game was interrupted, see you!")
  }

  onkeydown(keyCode) {
    switch(keyCode) {
      case Game.KEY.RETURN:
        if (this.cfg.multi) 
          this.startDoublePlayer();
        else
          this.startSinglePlayer();
        break;
      case Game.KEY.ESC:    this.stop(true);             break;
      case Game.KEY.Q:      this.myPaddle.moveUp();    break;
      case Game.KEY.A:      this.myPaddle.moveDown();  break;
      case Game.KEY.P:      if (!this.cfg.multi)  this.opponentPaddle.moveUp();  break;
      case Game.KEY.L:      if (!this.cfg.multi)  this.opponentPaddle.moveDown();  break;
    }
  }
  
  onkeyup(keyCode) {
    switch(keyCode) {
      case Game.KEY.Q:  this.myPaddle.stopMovingUp();    break;
      case Game.KEY.A:  this.myPaddle.stopMovingDown();  break;
      case Game.KEY.P:  if (!this.cfg.multi)  this.opponentPaddle.stopMovingUp();  break;
      case Game.KEY.L:  if (!this.cfg.multi)  this.opponentPaddle.stopMovingDown();  break;
    }
  }

  onWindowBlur() {
    this.myPaddle.stopMovingUp();
    this.myPaddle.stopMovingDown();
    if (!this.cfg.multi)  this.opponentPaddle.stopMovingUp();
    if (!this.cfg.multi)  this.opponentPaddle.stopMovingDown();
  }

//==============================================================================
// COURT
//==============================================================================
  
  static Court = class {
    
    static DIGITS = [
      [1, 1, 1, 0, 1, 1, 1], // 0
      [0, 0, 1, 0, 0, 1, 0], // 1
      [1, 0, 1, 1, 1, 0, 1], // 2
      [1, 0, 1, 1, 0, 1, 1], // 3
      [0, 1, 1, 1, 0, 1, 0], // 4
      [1, 1, 0, 1, 0, 1, 1], // 5
      [1, 1, 0, 1, 1, 1, 1], // 6
      [1, 0, 1, 0, 0, 1, 0], // 7
      [1, 1, 1, 1, 1, 1, 1], // 8
      [1, 1, 1, 1, 0, 1, 0]  // 9
    ];

    constructor(pong) {
      var w  = pong.width;
      var h  = pong.height;
      var ww = pong.cfg.wallWidth;

      this.ww    = ww;
      this.walls = [];
      this.walls.push({x: 0, y: 0,      width: w, height: ww});
      this.walls.push({x: 0, y: h - ww, width: w, height: ww});
      var nMax = (h / (ww*2));
      for(var n = 0 ; n < nMax ; n++) { // draw dashed halfway line
        this.walls.push({x: (w / 2) - (ww / 2), 
                        y: (ww / 2) + (ww * 2 * n), 
                        width: ww, height: ww});
      }

      var sw = 3*ww;
      var sh = 4*ww;
      this.score1 = {x: 0.5 + (w/2) - 1.5*ww - sw, y: 2*ww, w: sw, h: sh};
      this.score2 = {x: 0.5 + (w/2) + 1.5*ww,      y: 2*ww, w: sw, h: sh};
    }

    draw(ctx, scorePlayer1, scorePlayer2) {
      ctx.fillStyle = Pong.Colors.walls;
      for(var n = 0 ; n < this.walls.length ; n++)
        ctx.fillRect(this.walls[n].x, this.walls[n].y, this.walls[n].width, this.walls[n].height);
      this.drawDigit(ctx, scorePlayer1, this.score1.x, this.score1.y, this.score1.w, this.score1.h);
      this.drawDigit(ctx, scorePlayer2, this.score2.x, this.score2.y, this.score2.w, this.score2.h);
    }

    drawDigit(ctx, n, x, y, w, h) {
      ctx.fillStyle = Pong.Colors.score;
      var dh = this.ww*4/5;
      var dw = dh;
      var blocks = Pong.Court.DIGITS[n];
      if (blocks[0])
        ctx.fillRect(x, y, w, dh);
      if (blocks[1])
        ctx.fillRect(x, y, dw, h/2);
      if (blocks[2])
        ctx.fillRect(x+w-dw, y, dw, h/2);
      if (blocks[3])
        ctx.fillRect(x, y + h/2 - dh/2, w, dh);
      if (blocks[4])
        ctx.fillRect(x, y + h/2, dw, h/2);
      if (blocks[5])
        ctx.fillRect(x+w-dw, y + h/2, dw, h/2);
      if (blocks[6])
        ctx.fillRect(x, y+h-dh, w, dh);
    }
  };

//==============================================================================
// PADDLE
//==============================================================================

  static Paddle = class {

    constructor(pong, rhs) {
      this.pong   = pong;
      this.width  = pong.cfg.paddleWidth;
      this.height = pong.cfg.paddleHeight;
      this.minY   = pong.cfg.wallWidth;
      this.maxY   = pong.height - pong.cfg.wallWidth - this.height;
      this.speed  = (this.maxY - this.minY) / pong.cfg.paddleSpeed;
      this.x      = rhs ? pong.width - this.width : 0;
      this.y      = this.minY + (this.maxY - this.minY)/2;
      this.left   = this.x;
      this.right  = this.left + this.width;
      this.bottom = this.y;
      this.top    = this.y + this.height;
      this.setpos(this.x, this.y);
      this.setdir(0);
    }

    setpos(x, y) {
      this.x      = x;
      this.y      = y;
      this.left   = this.x;
      this.right  = this.left + this.width;
      this.top    = this.y;
      this.bottom = this.y + this.height;
    }

    setdir(dy) {
      this.up   = (dy < 0 ? -dy : 0);
      this.down = (dy > 0 ?  dy : 0);
    }

    update(dt) {
      var amount = this.down - this.up;
      if (amount != 0) {
        var y = this.y + (amount * dt * this.speed);
        if (y < this.minY)
          y = this.minY;
        else if (y > this.maxY)
          y = this.maxY;
        this.setpos(this.x, y);
      }
      return amount;
    }

    draw(ctx) {
      ctx.fillStyle = Pong.Colors.walls;
      ctx.fillRect(this.x, this.y, this.width, this.height);
    }

    moveUp() { this.up   = 1; }
    moveDown() { this.down = 1; }
    stopMovingUp() { this.up   = 0; }
    stopMovingDown() { this.down = 0; }
  };

//==============================================================================
// BALL
//==============================================================================

  static Ball = class {

    constructor(pong) {
      this.pong       = pong;
      this.radius     = pong.cfg.ballRadius;
      this.minX       = this.radius;
      this.maxX       = pong.width - this.radius;
      this.minY       = pong.cfg.wallWidth + this.radius;
      this.maxY       = pong.height - pong.cfg.wallWidth - this.radius;
      this.speed      = (this.maxX - this.minX) / pong.cfg.ballSpeed;
      this.accel      = pong.cfg.ballAccel;
      this.velocityIn = 10;
      this.initialX   = (this.maxX - this.minX) / 2 + this.radius;
      this.initialY   = (this.maxY - this.minY) / 2 + this.radius;
      this.direction  = { x : 0, y : 0};
    }

    random(min, max) {
      return (Math.random() * (max - min) + min);
    }

    isCollision(paddle) {
      return (
        this.left <= paddle.right &&
        this.right >= paddle.left &&
        this.top <= paddle.bottom &&
        this.bottom >= paddle.top
      );
    }

    isUpCollision(paddle) {
      return (
        this.right > paddle.left &&
        this.left < paddle.right &&
        (this.top <= paddle.top && this.bottom > paddle.top) // Ball hits the top
        //  (this.bottom >= paddle.bottom && this.top < paddle.bottom)) // Ball hits the bottom
    );
    }
    
    isDownCollision(paddle) {
      return (
        this.right > paddle.left &&
        this.left < paddle.right &&
        // (this.top <= paddle.top && this.bottom > paddle.top) // Ball hits the top
         (this.bottom >= paddle.bottom && this.top < paddle.bottom) // Ball hits the bottom
    );
    }

    reset() {
      this.setpos(this.initialX, this.initialY);
      this.setdir(this.speed, this.speed);
      this.direction.x = 0;
      while (
        Math.abs(this.direction.x) <= 0.5 ||
        Math.abs(this.direction.x) >= 0.8
      ) {
        const heading = this.random(0, 2 * Math.PI)
        this.direction = { x: Math.cos(heading), y: Math.sin(heading) }
      }
      this.velocity = this.pong.cfg.ballVelocity;
    }

    update(dt, leftPaddle, rightPaddle) {
      this.x += this.direction.x * this.velocity * dt;
      // this.setpos(this.x, this.y);
      this.y += this.direction.y * this.velocity * dt;
      // this.setpos(this.x, this.y);
      this.velocity += (this.pong.cfg.ballVelocityIncrease * dt * 0.5);
      
      if (this.y <= this.minY) {
        this.direction.y = Math.abs(this.direction.y);
        // this.setpos(this.x, this.y);
      }
      else if (this.y >= this.maxY) {
        this.direction.y = -Math.abs(this.direction.y);
        // this.setpos(this.x, this.y);
      }
      
      else if (this.isCollision(leftPaddle)) {
        // if (this.isUpCollision(leftPaddle)) 
        //   this.direction.y = -Math.abs(this.direction.y);
        // else if (this.isDownCollision(leftPaddle))
        //   this.direction.y = Math.abs(this.direction.y);
        // else
        this.direction.x = Math.abs(this.direction.x); // Ball hits the side of the paddle
        // this.setpos(this.x, this.y);
      }
      
      else if (this.isCollision(rightPaddle)) {
        // if (this.isUpCollision(rightPaddle))
        //   this.direction.y -Math.abs(this.direction.x);
        // else if (this.isDownCollision(rightPaddle))
        //   this.direction.y = Math.abs(this.direction.y);
        // else
        this.direction.x = -Math.abs(this.direction.x); // Ball hits the side of the paddle
        // this.setpos(this.x, this.y);
      }
      this.setpos(this.x, this.y);
    }
    
    setpos(x, y) {
      this.x      = x;
      this.y      = y;
      this.left   = this.x - this.radius;
      this.top    = this.y - this.radius;
      this.right  = this.x + this.radius;
      this.bottom = this.y + this.radius;
    }
    
    setdir(dx, dy) {
      this.dx = dx;
      this.dy = dy;
    }

    draw(ctx) {
      var h = this.radius * 2;
      var w = h; 
      ctx.fillStyle = Pong.Colors.ball;
      ctx.fillRect(this.x - this.radius, this.y - this.radius, w, h);
    }
  };
}
