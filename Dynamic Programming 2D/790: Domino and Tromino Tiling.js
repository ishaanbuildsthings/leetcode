// https://leetcode.com/problems/domino-and-tromino-tiling/
// Difficulty: Medium
// Tags: Dynamic Programming 2d

// Problem
/*
You have two types of tiles: a 2 x 1 domino shape and a tromino shape. You may rotate these shapes.


Given an integer n, return the number of ways to tile an 2 x n board. Since the answer may be very large, return it modulo 109 + 7.

In a tiling, every square must be covered by a tile. Two tilings are different if and only if there are two 4-directionally adjacent cells on the board such that exactly one of the tilings has both squares occupied by a tile.
*/

// Solution, O(n) time, O(n) space
/*
For each width in n, we have 3 possible states, no filled, the top is filled, or the bottom. Just standard dp.
*/

const MOD = 10 ** 9 + 7;
var numTilings = function (n) {
  // memo[l][state] gives us the answer to that sub problem
  // states are: 0 = empty, 1 = top filled, 2 = bottom filled
  const memo = new Array(n).fill().map(() => new Array(3).fill(-1));

  function dp(l, state) {
    // base cases
    if (l === n) {
      // if we used a tromino to fill two at once
      return 1;
    }
    // one column left
    if (l === n - 1) {
      if (state === 0) {
        return 1;
      }
      return 0;
    }

    if (memo[l][state] !== -1) {
      return memo[l][state];
    }

    let resultForThis;

    // if we are empty, we can place a --, a _ _, a |, or 2 trominos
    if (state === 0) {
      const topPlaced = dp(l + 2, 0) % MOD; // only solution is to put a bottom tromino
      const verticalPlaced = dp(l + 1, 0) % MOD;
      const topTrominoPlaced = dp(l + 1, 1) % MOD;
      const bottomTrominoPlaced = dp(l + 1, 2) % MOD;
      resultForThis =
        (topPlaced + verticalPlaced + topTrominoPlaced + bottomTrominoPlaced) %
        MOD;
    }

    // if top is filled, we can place a _ _, or a tromino
    else if (state === 1) {
      const bottomPlaced = dp(l + 1, 2) % MOD;
      const trominoPlaced = dp(l + 2, 0) % MOD;
      resultForThis = (bottomPlaced + trominoPlaced) % MOD;
    }

    // if bottom is filled, we can place a --, or a tromino
    else if (state === 2) {
      const topPlaced = dp(l + 1, 1) % MOD;
      const trominoPlaced = dp(l + 2, 0) % MOD;
      resultForThis = (topPlaced + trominoPlaced) % MOD;
    }
    memo[l][state] = resultForThis;
    return resultForThis;
  }

  return dp(0, 0);
};
