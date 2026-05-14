// https://leetcode.com/problems/painting-a-grid-with-three-different-colors/description/
// difficulty: hard
// tags: dynamic programming 2d, backtracking

// Problem
/*
You are given two integers m and n. Consider an m x n grid where each cell is initially white. You can paint each cell red, green, or blue. All cells must be painted.

Return the number of ways to color the grid with no two adjacent cells having the same color. Since the answer can be very large, return it modulo 109 + 7.
*/

// Solution, O(n*m* types of vertical strips) time, O(vertical strip types * n + vertical strip types * m) space
/*
Given the constraints on one dimension are small, first use backtracking to generate all possible vertical strips of colors. We will just say this is a constant time operation since it's bounded pretty tightly, but it is a function of the height of the matrix.

Then, for each row, we can include future rows that don't collide with the previous one. We iterate through all possible vertical strip types (and their lengths which is up to 5), and test them all.

This solution works well since we only have to consider the previous m cells rather than all cells or all diagonal cells or anything like that.
*/

const MOD = 10 ** 9 + 7;

var colorTheGrid = function (m, n) {
  const COLORS = ["r", "g", "b"];

  const verticals = [];
  function backtrack(currentColors) {
    if (currentColors.length === m) {
      verticals.push(currentColors.join(""));
      return;
    }

    for (const color of COLORS) {
      if (currentColors[currentColors.length - 1] !== color) {
        currentColors.push(color);
        backtrack(currentColors);
        currentColors.pop();
      }
    }
  }

  backtrack([]);

  // memo[prev vertical][i] solves the answer to the [i:] subproblem given a previous vertical
  const memo = new Array(verticals.length)
    .fill()
    .map(() => new Array(n).fill(-1));

  // make a dummy prefix dp to handle the initial case
  verticalLength = verticals[0].length;
  verticals[-1] = [];
  for (let i = 0; i < verticalLength; i++) {
    verticals[-1].push("w");
  }

  function dp(prevVerticalIndex, i) {
    // base case, we finished all columns
    if (i === n) {
      return 1;
    }

    if (prevVerticalIndex !== -1 && memo[prevVerticalIndex][i] !== -1) {
      return memo[prevVerticalIndex][i];
    }

    let resultForThis = 0;

    const prevVertical = verticals[prevVerticalIndex];

    for (
      let verticalIndex = 0;
      verticalIndex < verticals.length;
      verticalIndex++
    ) {
      const vertical = verticals[verticalIndex];
      let adjacentColorsFound = false;
      for (let j = 0; j < vertical.length; j++) {
        if (vertical[j] === prevVertical[j]) {
          adjacentColorsFound = true;
          break;
        }
      }
      if (!adjacentColorsFound) {
        resultForThis = (resultForThis + dp(verticalIndex, i + 1)) % MOD;
      }
    }

    if (prevVerticalIndex !== -1) {
      memo[prevVerticalIndex][i] = resultForThis;
    }

    return resultForThis;
  }

  return dp(-1, 0);
};
