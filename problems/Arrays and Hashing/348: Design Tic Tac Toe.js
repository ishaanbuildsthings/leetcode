// https://leetcode.com/problems/design-tic-tac-toe/description/
// Difficulty: Medium

// Problem
/*
Assume the following rules are for the tic-tac-toe game on an n x n board between two players:

A move is guaranteed to be valid and is placed on an empty block.
Once a winning condition is reached, no more moves are allowed.
A player who succeeds in placing n of their marks in a horizontal, vertical, or diagonal row wins the game.
Implement the TicTacToe class:

TicTacToe(int n) Initializes the object the size of the board n.
int move(int row, int col, int player) Indicates that the player with id player plays at the cell (row, col) of the board. The move is guaranteed to be a valid move, and the two players alternate in making moves. Return
0 if there is no winner after the move,
1 if player 1 is the winner after the move, or
2 if player 2 is the winner after the move.
 */

// Solution 1, O(n) space for the constructor, and O(1) time for move
/*
Constructor: Create a rows array that maintains a count for how many of player 1's moves are in a given index in that array. For instance if rows[2] = 5, player 1 has a +5 advantage on the 3rd row. If player 2 makes a move, the count decreases. Whenever the count reaches +n or -n we know we have a win. Also maintain a variable for each diagonal, and an array for the columns. Whenever a move is made update the appropriate values and determine if there is a win.
*/

var TicTacToe = function (n) {
  this.rows = new Array(n).fill(null); // the ith index cell represents how many times a player has played in that row, for instance if 5, player1 has a +5 advantage, if -3, player 2 has a +3 advantage, whenever the advantage reaches n, there is a win
  this.cols = new Array(n).fill(null);
  this.majorDiag = 0;
  this.minorDiag = 0;
  this.n = n;
};

TicTacToe.prototype.move = function (row, col, player) {
  // check rows
  if (player === 1) {
    this.rows[row]++;
  } else {
    this.rows[row]--;
  }
  if (this.rows[row] === this.n) {
    return 1;
  } else if (this.rows[row] === -1 * this.n) {
    return 2;
  }

  // check columns
  if (player === 1) {
    this.cols[col]++;
  } else {
    this.cols[col]--;
  }
  if (this.cols[col] === this.n) {
    return 1;
  } else if (this.cols[col] === -1 * this.n) {
    return 2;
  }

  // check major diag
  if (row === col) {
    if (player === 1) {
      this.majorDiag++;
    } else {
      this.majorDiag--;
    }
  }
  if (this.majorDiag === this.n) {
    return 1;
  } else if (this.majorDiag === -1 * this.n) {
    return 2;
  }

  // check minor diag
  if (row + col + 1 === this.n) {
    if (player === 1) {
      this.minorDiag++;
    } else {
      this.minorDiag--;
    }
  }
  if (this.minorDiag === this.n) {
    return 1;
  } else if (this.minorDiag === -1 * this.n) {
    return 2;
  }

  return 0;
};

// Solution 2, O(n^2) space for the constructor, and O(1) time for the move

/*
Constructor: Create an n x n board. For move, check the row, column, and diagonals the move was in, and see if it created a win.
*/
var TicTacToe = function (n) {
  this.board = new Array(n).fill().map(() => new Array(n).fill(null)); // create an n x n board
};

TicTacToe.prototype.move = function (row, col, player) {
  // place the move
  this.board[row][col] = player; // either a 1 or 2

  // determine enemy
  let enemyPlayer;
  if (player === 1) {
    enemyPlayer = 2;
  } else {
    enemyPlayer = 1;
  }

  // check row
  let rowWin = true;
  for (let colIterate = 0; colIterate < this.board.length; colIterate++) {
    const cellValue = this.board[row][colIterate];
    if (cellValue === null || cellValue === enemyPlayer) {
      rowWin = false;
      break;
    }
  }

  if (rowWin) {
    return player;
  }

  // check column
  let colWin = true;
  for (let rowIterate = 0; rowIterate < this.board.length; rowIterate++) {
    const cellValue = this.board[rowIterate][col];
    if (cellValue === null || cellValue === enemyPlayer) {
      colWin = false;
      break;
    }
  }

  if (colWin) {
    return player;
  }

  // check major diagonal
  let majorDiagWin = true;
  for (let i = 0; i < this.board.length; i++) {
    const cellValue = this.board[i][i];
    if (cellValue === null || cellValue === enemyPlayer) {
      majorDiagWin = false;
      break;
    }
  }

  if (majorDiagWin) {
    return player;
  }

  // check minor diagonal
  let minorDiagWin = true;
  for (let i = 0; i < this.board.length; i++) {
    const rowIndex = i;
    const colIndex = this.board.length - i - 1;
    const cellValue = this.board[rowIndex][colIndex];
    if (cellValue === null || cellValue === enemyPlayer) {
      minorDiagWin = false;
    }
  }

  if (minorDiagWin) {
    return player;
  }

  return 0;
};

/**
 * Your TicTacToe object will be instantiated and called as such:
 * var obj = new TicTacToe(n)
 * var param_1 = obj.move(row,col,player)
 */
