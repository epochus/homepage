"use strict";

var canvas;
var ctx;
var dim = 4;
var HEIGHT;
var WIDTH;

var tiles;
var TILE_SIZE = 100;
var PADDING = 1;
var tileColor = "#2980b9"; // blue
var backColor = "#7CE0F9"; // glass-gall

var timeoutId = 0;
var activeListen = false;

var click = new Object;
click.row = 0;
click.col = 0;

var empty = new Object;
empty.row = 0;
empty.col = 0;

var preset;
var board;
var solved = false;

// Animation
var x;
var y;
var dx;
var dy;
var x_move = false;
var y_move = false;
var x_empty = 0;
var y_empty = 0;

var moveStr = "";
var buttons;
var complete_txt;

function init() {
  canvas = document.getElementById("canvas");
  ctx = canvas.getContext("2d");
  HEIGHT = canvas.height;
  WIDTH = canvas.width;
  buttons = document.getElementsByClassName("btn");
  buttons[0].disabled = false;
  buttons[1].disabled = false;
  buttons[2].disabled = false;
  
  preset = shuffle();
  setBoard(preset);
  drawTiles();
}

/* Creates a rectangle with number  */
function createTile(x, y, w, h, num) {
  ctx.fillStyle = tileColor;
  ctx.beginPath();
  ctx.rect(x, y, w, h);
  ctx.closePath();
  ctx.fill();
  ctx.fillStyle = "white";
  ctx.font = "80px Trebuchet MS";
  var x_dist = 10;
  if (num < 10)
    x_dist += 20;
  var numText = num.toString();
  ctx.fillText(num.toString(), x_dist+x, 80+y);
  ctx.lineWidth = 1;
  ctx.strokeStyle = "black";
  ctx.stroke();
}

/* Assigns numbers to each tile */
function setBoard(preset) {
  board = new Array(dim);
  for (var i = 0; i < dim; i++) {
    board[i] = new Array(dim);
    for (var j = 0; j < dim; j++) {
      board[i][j] = new Object;
      board[i][j].row = i;
      board[i][j].col = j;
      board[i][j].val = preset[i][j];
      if (board[i][j].val == 0) {
        empty.col = j;
        empty.row = i;
      }
    }
  }
}

/* Draws the tiles with each number */
function drawTiles() {
  clear();
  for (var i = 0; i < dim; i++) {
    for (var j = 0; j < dim; j++) {
      if (j != empty.col || i != empty.row) {
        createTile((j * (TILE_SIZE + PADDING)) + PADDING,
            (i * (TILE_SIZE + PADDING)) + PADDING,
            TILE_SIZE, TILE_SIZE, board[i][j].val);
      }
    }
  }
}

/* Returns the Manhattan distance between two tiles */
function distance(x1, y1, x2, y2) {
  return Math.abs(x1-x2) + Math.abs(y1-y2);
}

/* Clears the entire board */
function clear() {
  ctx.clearRect(0, 0, WIDTH, HEIGHT);
}

/* Enables solve button and changes text */
function resetSolveBtn() {
  buttons[2].disabled = false;
  buttons[2].innerText = "Solve";
}

/* Resets to a new board */
function scramble() {
  resetSolveBtn();
  init();
}

/* Resets the board without shuffling board */
function resetBoard() {
  resetSolveBtn();
  setBoard(preset);
  drawTiles();
}

/* Creates a 2d-array of the current board */
function makeMatrix(dim) {
  var arr = [];

  for (var i = 0; i < dim; i++) {
    arr.push([]);
    arr[i].push(new Array(dim));

    for (var j = 0; j < dim; j++) {
      arr[i][j] = board[i][j].val;
    }
  }
  return arr;
}

/* Sends current board to <app_name>/views.py */
function createPost() {
  var currentBoard = makeMatrix(dim);
  var msg = {'board': JSON.stringify(currentBoard)};

  $.ajax({
    url: 'fifteen-puzzle/solve',
    type: 'GET',
    data: msg,
    success: function(data) {
      moveStr = data['result'];
      aiSolve(moveStr);
    },
    failure: function(data) {
      console.log('A problem occurred.', data);
    }
  });
}

/* Checks if board is solved */
function isSolved() {
  for (var row = 0; row < dim; row++) {
    for (var col = 0; col < dim; col++) {
      var solved_value = col + (dim * row);
      if (board[row][col].val != solved_value) {
        return false;
      }
    }
  }

  return true;
}

/* Wrapper function for keydown events */
function processKeyCode(evt) {
  if (!activeListen) {
    activeListen = true;
    var keyCode = evt.keyCode;
    var promise = moveTile(keyCode);
    promise.done(function() {
      activeListen = false;
    });
  }
}

/* Moves a tile in a direction with animation */
function moveTile(keyCode) {
  var deferred = $.Deferred();

  setTimeout(function() {
  // Left
  if (keyCode == 37) {
    if (empty.col != dim-1) {
      click.row = empty.row;
      click.col = empty.col+1;
      dx = -10;
      dy = 0;
      x_move = true;
      y_move = false;
    }
  }
  // Up
  else if (keyCode == 38) {
    if (empty.row != dim-1) {
      click.row = empty.row+1;
      click.col = empty.col;
      dx = 0;
      dy = -10;
      x_move = false;
      y_move = true;

    }
  }
  // Right
  else if (keyCode == 39) {
    if (empty.col != 0) {
      click.row = empty.row;
      click.col = empty.col-1;
      dx = 10;
      dy = 0;
      x_move = true;
      y_move = false;
    }
  }
  // Down
  else if (keyCode == 40) {
    if (empty.row != 0) {
      click.row = empty.row-1;
      click.col = empty.col;
      dx = 0;
      dy = 10;
      x_move = false;
      y_move = true;
    }
  }

  var dist = distance(click.col, click.row, empty.col, empty.row);
  if (dist == 1) {
    animate(empty, click);
  }

  deferred.resolve();
  }, 100);

  return deferred.promise();
}

/* Swaps value and position and checks if the board is solved*/
function update(empty, click) {
  // swaps values
  var temp = board[empty.row][empty.col].val;
  board[empty.row][empty.col].val = board[click.row][click.col].val;
  board[click.row][click.col].val = temp;

  // Sets position for empty tile
  empty.col = click.col;
  empty.row = click.row;

  solved = isSolved();
  if (solved) {
    buttons[0].disabled = "";
    buttons[1].disabled = "";
    buttons[2].innerText = "Completed";

    document.addEventListener("keydown", processKeyCode);
    canvas.onmousedown = function(evt) {
      click.row = Math.floor((evt.pageY - this.offsetTop) / TILE_SIZE);
      click.col = Math.floor((evt.pageX - this.offsetLeft) / TILE_SIZE);
      var dist = distance(click.col, click.row, empty.col, empty.row);
      if (dist == 1) {
        update(empty, click);
        drawTiles();
      }
    }
  }
}

/* Slides the tile when keyboard is pressed */
function animate(empty, click) {
  x = click.col * (TILE_SIZE + PADDING) + PADDING;
  y = click.row * (TILE_SIZE + PADDING) + PADDING;
  x_empty = empty.col * (TILE_SIZE + PADDING) + PADDING;
  y_empty = empty.row * (TILE_SIZE + PADDING) + PADDING;

  timeoutId = setTimeout(draw, 1);
}

/* Clears rect and creates tile until at desired position */
function draw() {
  ctx.fillStyle = backColor;
  ctx.clearRect(x,y, TILE_SIZE, TILE_SIZE);
  x += dx;
  y += dy;
  if (x > x_empty || x < x_empty)
    x = x_empty;
  if (y > y_empty || y < y_empty)
    y = y_empty;
  createTile(x, y, TILE_SIZE, TILE_SIZE, board[click.row][click.col].val);
  if (y == y_empty && y_move) {
    update(empty, click);
  }
  else if (x == x_empty && x_move) {
    update(empty, click);
  }
  else
    timeoutId = setTimeout(draw, 1);
}

/* Solves board given an array of (l,u,r,d) letters */
function aiSolve(arr) {
  if (arr.length == 0)
    update(empty, click);
  else {
      // Disables buttons
      buttons[0].disabled = "disable";
      buttons[1].disabled = "disable";
      buttons[2].disabled = "disable";
      buttons[2].innerText = "Solving...";

      // Disables mouse and keyboard
      document.removeEventListener("keydown", processKeyCode);
      canvas.onmousedown = function(evt) {
        evt.preventDefault();
      }

      var defr = (new $.Deferred()).resolve();
      arr.forEach(function(letter) {
        defr = defr.pipe(function() {
          var keycode;
          // letters represented movement of empty tile,
          // now causes sliding in opposite direction
          if (letter == 'l')
            keycode = 39;
          else if (letter == 'u')
            keycode = 40;
          else if (letter == 'r')
            keycode = 37;
          else if (letter == 'd')
            keycode = 38;
          var promise = moveTile(keycode);
          return promise.done(function() {
            // do nothing
          });
        });
      });
  }
}

/* Returns a random integer between min (included) and max (excluded) */
function getRandomInt(min, max) {
  return Math.floor(Math.random() * (max-min)) + min;
}

/* Returns a string with a pattern that repeats count times */
function repeat(pattern, count) {
  if (count < 1)
    return '';
  var result = "";
  while (count > 1) {
    if (count & 1)
      result += pattern;
    count >>= 1
    pattern += pattern;
  }
  return result + pattern;
}

/* Returns a shuffled 2d-array */
function shuffle() {
  var zeroRow = 0;
  var zeroCol = 0;
  var state =  [[0,1,2,3],
                [4,5,6,7],
                [8,9,10,11],
                [12,13,14,15]];

  var lmoves = getRandomInt(50, 101);
  var rmoves = getRandomInt(50, 101);
  var umoves = getRandomInt(50, 101);
  var dmoves = getRandomInt(50, 101);

  var lefts = repeat("l", lmoves);
  var rights = repeat("r", rmoves);
  var ups = repeat("u", umoves);
  var downs = repeat("d", dmoves);

  var translations = lefts + rights + ups + downs;

  // Fisher-Yates shuffle
  var moveList = translations.split('');
  for (var i = moveList.length; i > 0;) {
    var random = parseInt(Math.random() * i);
    var temp = moveList[--i];
    moveList[i] = moveList[random];
    moveList[random] = temp;
  }

  // Swaps values in state array
  for (var i = 0; i < moveList.length; i++) {
    if (moveList[i] == "l" && zeroCol != 0) {
      var temp = state[zeroRow][zeroCol-1];
      state[zeroRow][zeroCol] = temp;
      state[zeroRow][zeroCol-1] = 0;
      zeroCol -= 1;
    }
    else if (moveList[i] == "u" &&  zeroRow != 0) {
      var temp = state[zeroRow-1][zeroCol];
      state[zeroRow][zeroCol] = temp;
      state[zeroRow-1][zeroCol] = 0;
      zeroRow -= 1;
    }
    else if (moveList[i] == "r" && zeroCol != dim-1) {
      var temp = state[zeroRow][zeroCol+1];
      state[zeroRow][zeroCol] = temp;
      state[zeroRow][zeroCol+1] = 0;
      zeroCol += 1;
    }
    else if (moveList[i] == "d" && zeroRow != dim-1) {
      var temp = state[zeroRow+1][zeroCol];
      state[zeroRow][zeroCol] = temp;
      state[zeroRow+1][zeroCol] = 0;
      zeroRow += 1;
    }
  }

  return state;
}

/* Waits until content is loaded */
$(window).load(function() {
  init();

  // Prevents browser from scrolling
  window.addEventListener("keydown", function(e) {
    // space and arrow keys
    if([32, 37, 38, 39, 40].indexOf(e.keyCode) > -1) {
        e.preventDefault();
    }
  }, false);

  /* Executes when left mouse button is pressed */
  canvas.onmousedown = function(evt) {
    click.row = Math.floor((evt.pageY - this.offsetTop) / TILE_SIZE);
    click.col = Math.floor((evt.pageX - this.offsetLeft) / TILE_SIZE);
    var dist = distance(click.col, click.row, empty.col, empty.row);
    if (dist == 1) {
      update(empty, click);
      drawTiles();
    }
  }

  /* Handles keypresses */
  document.addEventListener("keydown", processKeyCode);
});