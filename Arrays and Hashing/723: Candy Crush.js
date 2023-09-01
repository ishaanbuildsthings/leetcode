// https://leetcode.com/problems/candy-crush/description/
// Difficulty: Medium

// Problem
/*
This question is about implementing a basic elimination algorithm for Candy Crush.

Given an m x n integer array board representing the grid of candy where board[i][j] represents the type of candy. A value of board[i][j] == 0 represents that the cell is empty.

The given board represents the state of the game following the player's move. Now, you need to restore the board to a stable state by crushing candies according to the following rules:

If three or more candies of the same type are adjacent vertically or horizontally, crush them all at the same time - these positions become empty.
After crushing all candies simultaneously, if an empty space on the board has candies on top of itself, then these candies will drop until they hit a candy or bottom at the same time. No new candies will drop outside the top boundary.
After the above steps, there may exist more candies that can be crushed. If so, you need to repeat the above steps.
If there does not exist more candies that can be crushed (i.e., the board is stable), then return the current board.
You need to perform the above rules until the board becomes stable, then return the stable board.
*/

// Solution
/*
I just repeated crushing candies, and then dropping them, until a crush yielded no changes. The steps are somewhat slow, and can be improved with some different structures and preprocessing. Also the `blocked` stuff in the crushCandies function can be simplifed a lot.
*/

/**
 * @param {number[][]} board
 * @return {number[][]}
 */
var candyCrush = function (board) {
  const HEIGHT = board.length;
  const WIDTH = board[0].length;

  // returns false if nothing can be crushed
  function crushCandies() {
    let changeFound = false;

    const clearedCells = new Set(); // holds string keys

    for (let r = 0; r < HEIGHT; r++) {
      for (let c = 0; c < WIDTH; c++) {
        const key = `${r},${c}`;
        if (clearedCells.has(key)) {
          continue;
        }
        // ignore previously crushed cells
        if (board[r][c] === 0) {
          continue;
        }

        // check up and down
        const upAndDownCells = [[r, c]];

        let diff = 0;
        let upBlocked = false;
        let downBlocked = false;
        while (true) {
          diff++;

          let continuationFound = false;

          // if above is in range, not blocked, and the same cell, add it
          if (
            r - diff >= 0 &&
            board[r - diff][c] === board[r][c] &&
            !upBlocked
          ) {
            continuationFound = true;
            upAndDownCells.push([r - diff, c]);
          } else {
            upBlocked = true;
          }
          if (
            r + diff < HEIGHT &&
            board[r + diff][c] === board[r][c] &&
            !downBlocked
          ) {
            continuationFound = true;
            upAndDownCells.push([r + diff, c]);
          } else {
            downBlocked = true;
          }

          if (!continuationFound) {
            break;
          }
        }

        // check left and right
        const leftAndRightCells = [[r, c]];
        let leftBlocked = false;
        let rightBlocked = false;

        diff = 0;
        while (true) {
          diff++;

          let continuationFound = false;

          // if the left cell is in range, not blocked, and the same cell, add it
          if (
            c - diff >= 0 &&
            board[r][c - diff] === board[r][c] &&
            !leftBlocked
          ) {
            continuationFound = true;
            leftAndRightCells.push([r, c - diff]);
          } else {
            leftBlocked = true;
          }
          if (
            c + diff < WIDTH &&
            board[r][c + diff] === board[r][c] &&
            !rightBlocked
          ) {
            continuationFound = true;
            leftAndRightCells.push([r, c + diff]);
          } else {
            rightBlocked = true;
          }

          if (!continuationFound) {
            break;
          }
        }

        // zero out the cleared cells
        if (upAndDownCells.length >= 3) {
          changeFound = true;
          for (const [vertRow, vertCol] of upAndDownCells) {
            const key = `${vertRow},${vertCol}`;
            clearedCells.add(key);
          }
        }
        if (leftAndRightCells.length >= 3) {
          changeFound = true;
          for (const [horizontalRow, horizontalCol] of leftAndRightCells) {
            const key = `${horizontalRow},${horizontalCol}`;
            clearedCells.add(key);
          }
        }
      }
    }

    for (const clearedCellKey of Array.from(clearedCells)) {
      const keyArr = clearedCellKey.split(",");
      const row = Number(keyArr[0]);
      const col = Number(keyArr[1]);
      board[row][col] = 0;
    }

    return changeFound;
  }

  function dropCandies() {
    for (let r = 0; r < HEIGHT; r++) {
      for (let c = 0; c < WIDTH; c++) {
        if (board[r][c] !== 0) {
          continue;
        }
        if (r === 0 || board[r - 1][c] === 0) {
          continue;
        }
        /* here, the cell is a 0 with candy above it */

        for (let rowIterator = r; rowIterator >= 1; rowIterator--) {
          const cellAbove = board[rowIterator - 1][c];
          // we found the gap at the top
          if (cellAbove === 0) {
            break;
          }
          board[rowIterator][c] = cellAbove;
          board[rowIterator - 1][c] = 0;
        }
      }
    }
  }

  while (true) {
    const changeFound = crushCandies();
    if (!changeFound) {
      return board;
    }

    dropCandies();
  }
};
