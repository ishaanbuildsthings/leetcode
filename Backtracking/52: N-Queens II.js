// https://leetcode.com/problems/n-queens-ii/description/
// Difficulty: Hard
// tags: backtracking

// Problem
/*
The n-queens puzzle is the problem of placing n queens on an n x n chessboard such that no two queens attack each other.

Given an integer n, return the number of distinct solutions to the n-queens puzzle.
*/

// Solution, O(n!) time and O(n) space for the set allocations.

/*
Similar to 51, n-queens. See that solution writeup as it is nearly the exact same. The only difference is we just store visited cols/diags in this problem, as opposed to the actual board, we just store sets of what we have visited.
*/

/**
 * @param {number} n
 * @return {number}
 */
var totalNQueens = function (n) {
  let result = 0;

  function backtrack(
    currentRow,
    visitedCols,
    visitedMinorDiags,
    visitedMajorDiags
  ) {
    // if we reached the out of bounds level, it means we successfully placed n queens, as otherwise we would have not called any other backtracks earlier on.
    if (currentRow === n) {
      result++;
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

      visitedCols.add(col);
      visitedMinorDiags.add(sum);
      visitedMajorDiags.add(diff);

      backtrack(
        currentRow + 1,
        visitedCols,
        visitedMinorDiags,
        visitedMajorDiags
      );

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
