// https://leetcode.com/problems/stone-game/description/
// Difficulty: Medium
// tags: dynamic programming 2d, range query

// Problem

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
