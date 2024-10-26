// https://leetcode.com/problems/stone-game/description/
// Difficulty: Medium
// tags: dynamic programming 2d, range query

// Problem
/*
Alice and Bob play a game with piles of stones. There are an even number of piles arranged in a row, and each pile has a positive integer number of stones piles[i].

The objective of the game is to end with the most stones. The total number of stones across all the piles is odd, so there are no ties.

Alice and Bob take turns, with Alice starting first. Each turn, a player takes the entire pile of stones either from the beginning or from the end of the row. This continues until there are no more piles left, at which point the person with the most stones wins.

Assuming Alice and Bob play optimally, return true if Alice wins the game, or false if Bob wins.
*/

// Solution, O(n^2) time and O(n^2) space
/*
We make a dp function that deduces how many stones can be won from the subarray [l, r]. We have two choices, either take piles[l], then the opponent can take [l+1, r] dp, or we take piles[r] and the opponent can take [l, r-1] dp. We have n^2 dps to fill. Initially, each dp took n time to fill, because to find how many stones we win, we would have to do a range sum, then subtract the dp the opponent makes, but with preprocessed range sum queries, we can get constant time for each dp cell.

We could also have tracked a turn order, and used a minimizer/maximizer style of play.
*/

var stoneGame = function (piles) {
  // stores information for the sum from [0, i], helps us do a range query for better time complexity
  const prefixSums = [];

  let runningSum = 0;
  for (let i = 0; i < piles.length; i++) {
    runningSum += piles[i];
    prefixSums[i] = runningSum;
  }
  prefixSums[-1] = 0; // if we range query from [0, x]

  let totalStones = piles.reduce((acc, val) => acc + val, 0);

  // stores how many stones a player can win from a given subarray, assuming they are going first
  const memo = new Array(piles.length)
    .fill()
    .map(() => new Array(piles.length).fill(-1));

  // returns how many stones a player gets from a given subarray
  function dp(l, r) {
    // base case, only one pile to chooes from
    if (l === r) {
      return piles[l];
    }

    if (memo[l][r] !== -1) {
      return memo[l][r];
    }

    const totalStonesInSubarray = prefixSums[r] - prefixSums[l - 1];

    // the total amount of stones we get if we take the left pile is the total amount of stones in all piles, minus the amount the opponent wins from [l + 1][r]
    const totalStonesIfWeTakeLeft = totalStonesInSubarray - dp(l + 1, r);
    const totalStonesIfWeTakeRight = totalStonesInSubarray - dp(l, r - 1);

    const mostStones = Math.max(
      totalStonesIfWeTakeLeft,
      totalStonesIfWeTakeRight
    );

    memo[l][r] = mostStones;
    return mostStones;
  }

  const stonesAliceGets = dp(0, piles.length - 1);
  if (stonesAliceGets > totalStones / 2) {
    return true;
  }

  return false;
};
