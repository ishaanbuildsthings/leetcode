// https://leetcode.com/problems/sudoku-solver/description/
// Difficulty: Hard
// tags: backtracking

// Problem
/*
Example:

Input: board = [["5","3",".",".","7",".",".",".","."],["6",".",".","1","9","5",".",".","."],[".","9","8",".",".",".",".","6","."],["8",".",".",".","6",".",".",".","3"],["4",".",".","8",".","3",".",".","1"],["7",".",".",".","2",".",".",".","6"],[".","6",".",".",".",".","2","8","."],[".",".",".","4","1","9",".",".","5"],[".",".",".",".","8",".",".","7","9"]]
Output: [["5","3","4","6","7","8","9","1","2"],["6","7","2","1","9","5","3","4","8"],["1","9","8","3","4","2","5","6","7"],["8","5","9","7","6","1","4","2","3"],["4","2","6","8","5","3","7","9","1"],["7","1","3","9","2","4","8","5","6"],["9","6","1","5","3","7","2","8","4"],["2","8","7","4","1","9","6","3","5"],["3","4","5","2","8","6","1","7","9"]]

Write a program to solve a Sudoku puzzle by filling the empty cells.

A sudoku solution must satisfy all of the following rules:

Each of the digits 1-9 must occur exactly once in each row.
Each of the digits 1-9 must occur exactly once in each column.
Each of the digits 1-9 must occur exactly once in each of the 9 3x3 sub-boxes of the grid.
The '.' character indicates empty cells.
*/

// Solution, O(9! ^ 9) time and O(1) space, or just O(1) time
/*
Backtracking. Maintain sets for each row, column, and box, to know which numbers we already have. Start at the first empty cell, try all valid numbers, then recurse on the next empty cell. If we cannot add a cell, we return false. If we can, we return the board. At a given state, when we recurse on a neighbor, if it returned true (meaning it returned the board), we return that. Each row takes at most 9! time as maybe every row is valid, and there are 9 rows, so 9! ^ 9 time.
*/

var solveSudoku = function (board) {
  // row[i] indicates numbers in that row
  const rows = new Array(9).fill().map(() => new Set());
  const cols = new Array(9).fill().map(() => new Set());
  const boxes = new Array(9).fill().map(() => new Set());

  // seed the initial sets
  for (let r = 0; r < 9; r++) {
    for (let c = 0; c < 9; c++) {
      if (board[r][c] === ".") {
        continue;
      }
      const val = board[r][c];

      rows[r].add(val);
      cols[c].add(val);

      // figure out which box we are in
      const boxRow = Math.floor(r / 3); // maps a row to 0, 1, 2
      const boxCol = Math.floor(c / 3);
      const boxNum = boxRow * 3 + boxCol; // WIDTH*row + col, standard hashing technique!

      boxes[boxNum].add(val);
    }
  }

  // tries different valid numbers for an empty cell, then backtracks to the next empty cell
  function backtrack(r, c) {
    // base case, we finished the board
    if (r === 9) {
      return board;
    }

    // we will need to recurse on the next empty slot, for each character we try in the current slot, calculate it once so we don't need to recalculate for each character
    let rowNum;
    let colNum;
    let cellFound = false;
    for (rowNum = r; rowNum < 9; rowNum++) {
      for (colNum = 0; colNum < 9; colNum++) {
        if (rowNum === r && colNum <= c) {
          continue;
        }
        if (board[rowNum][colNum] === ".") {
          cellFound = true;
          break;
        }
      }
      if (cellFound) {
        break;
      }
    }

    /* here, board[rowNum][colNum] is the next empty slot */

    const rowSet = rows[r];
    const colSet = cols[c];
    const boxSet = boxes[Math.floor(r / 3) * 3 + Math.floor(c / 3)];

    // try filling the cell with any valid number
    for (const char of "123456789") {
      if (rowSet.has(char) || colSet.has(char) || boxSet.has(char)) {
        continue;
      }

      // add changes
      board[r][c] = char;
      rowSet.add(char);
      colSet.add(char);
      boxSet.add(char);

      // test adjacent state
      const result = backtrack(rowNum, colNum);
      if (result) {
        return result;
      }

      // undo changes
      board[r][c] = ".";
      rowSet.delete(char);
      colSet.delete(char);
      boxSet.delete(char);
    }

    return false; // if we didn't get a valid board, we return false from this state
  }

  // find the first empty row + col
  for (let r = 0; r < 9; r++) {
    for (c = 0; c < 9; c++) {
      if (board[r][c] === ".") {
        return backtrack(r, c);
      }
    }
  }
};
