// https://leetcode.com/problems/n-queens/description/
// Difficulty: Hard
// tags: backtracking

// Problem
/*
Simplified:

Input: n = 4
Output: [[".Q..","...Q","Q...","..Q."],["..Q.","Q...","...Q",".Q.."]]
Explanation: There exist two distinct solutions to the 4-queens puzzle as shown above

Detailed:
The n-queens puzzle is the problem of placing n queens on an n x n chessboard such that no two queens attack each other.

Given an integer n, return all distinct solutions to the n-queens puzzle. You may return the answer in any order.

Each solution contains a distinct board configuration of the n-queens' placement, where 'Q' and '.' both indicate a queen and an empty space, respectively.
*/

// Solution, O(n!) time and O(n^2) space
/*
Allocate an empty board matrix. We will backtrack across each row. Meaning for any given row, place a queen in every column (if valid), then recurse on the next row with that state.

We have to track visited columns in a set, so we do not place queens in the same column as earlier. Similarly, we track visited major and minor diagonals, using methods detailed in the code comments (tracked via difference of row and column, and sum of row and column).

When our row number === n, it means we successfully backtracked through each row, placing a queen. We stringify the matrix and add it to the result.

There are n options for the queen in the first row, n-1 options for the queen in the second row, n-2 options for the queen in the third row, etc. This means the bumber of backtrack calls we make is upper bounded by n! (really less, because we also don't place queens in invalid diagonals). Supposedly, the number of valid solutions, S(n), grows much more slowly than the number of possible states to consider, F(n), so even though each solution takes n^2 time to serialize, it is dominated by n!. I am not sure about this though.

For space, we hold an n^2 matrix. This means even when our result is full / we found all valid combinations, we might still be searching and therefore have n^2 extra memory concurrently allocated.

I think instead of holding the entire board state, we could just hold a list of n coordinates that we currently have a queen at, and when we get a solution we construct a board from that. This might make our space complexity O(n).
*/

var solveNQueens = function (n) {
  const result = [];

  const currentBoard = new Array(n).fill().map((_) => new Array(n).fill(".")); // as we will need to return solutions of this form

  function backtrack(
    currentRow,
    visitedCols,
    visitedMinorDiags,
    visitedMajorDiags
  ) {
    // if we reached the out of bounds level, it means we successfully placed n queens, as otherwise we would have not called any other backtracks earlier on.
    if (currentRow === n) {
      const newValidState = [];
      for (const row of currentBoard) {
        const level = row.join("");
        newValidState.push(level);
      }
      result.push(newValidState);
      return;
    }
    // for a given row, try placing a queen at every column
    for (let col = 0; col < n; col++) {
      // don't backtrack to spots where the queen is in an occupied column
      if (visitedCols.has(col)) {
        continue;
      }

      const sum = currentRow + col;
      if (visitedMinorDiags.has(sum)) {
        continue;
      }

      const diff = currentRow - col;
      if (visitedMajorDiags.has(diff)) {
        continue;
      }

      currentBoard[currentRow][col] = "Q";
      visitedCols.add(col);
      visitedMinorDiags.add(sum);
      visitedMajorDiags.add(diff);

      backtrack(
        currentRow + 1,
        visitedCols,
        visitedMinorDiags,
        visitedMajorDiags
      );

      currentBoard[currentRow][col] = ".";
      visitedCols.delete(col);
      visitedMinorDiags.delete(sum);
      visitedMajorDiags.delete(diff);
    }
  }

  /*
    visitedCols is self-explanatory, any time we put a ueen in a column, we mark that column as visited, so that future queens cannot be placed.

    majorDiags (going down and right) are numbered by the diff between the row and the column. so the longest majorDiag, has a diff of 0. the one above it has a diff of -1, as the row is 1 less than the col, and so on.

    minorDiags (going up and right) are labeled by the sum of the row and column. so the main minor diag will always have a sum of n-1 for each element. for instance in a 3x3, the main minorDiag will consist of [2,0], [1,1], [0, 2], so the sum is 2.

    */

  backtrack(0, new Set(), new Set(), new Set());

  return result;
};
