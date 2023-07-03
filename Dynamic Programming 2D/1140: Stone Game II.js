// https://leetcode.com/problems/stone-game-ii/description/
// Difficulty: Medium
// tags: dynamic programming 2d, top down recursion

// Problem
/*
Alice and Bob continue their games with piles of stones.  There are a number of piles arranged in a row, and each pile has a positive integer number of stones piles[i].  The objective of the game is to end with the most stones.

Alice and Bob take turns, with Alice starting first.  Initially, M = 1.

On each player's turn, that player can take all the stones in the first X remaining piles, where 1 <= X <= 2M.  Then, we set M = max(M, X).

The game continues until all the stones have been taken.

Assuming Alice and Bob play optimally, return the maximum number of stones Alice can get.

Clarification, on a player's turn, they MUST take all stones in the first X piles.
*/

// Solution, O(n^3) time and O(n^2) space, top down recursion + memoization
/*

*/
var stoneGameII = function (piles) {
  // memo[l][m] represents the solution to the problem for the maximum amount of stones anyone can get from the subarray starting at `l`, with a given `m`
  // we need to make the `m` section piles.length + 1, because m is always 1 at the start, so if the pile length is 1, such as [1], then our possible `m` array is of length 1, meaning it only considers when m=0, i think
  const memo = new Array(piles.length)
    .fill()
    .map(() => new Array(piles.length + 1).fill(-1));

  function dp(l, m) {
    if (l === piles.length) {
      return 0;
    }
    if (memo[l][m] !== -1) {
      return memo[l][m];
    }

    let maxStonesWeCanGet = 0;

    // consider us taking some amount of the first piles, we gain some stones, and now leave our opponent with the problem to take the maximum remaining stones in a subproblem. so the maximum amount of stones WE could get is, across all different pile-taking amounts, the total amount of stones that we had presented to us, minus the max amount of stones our opponent could take from the subarray we leave them. this could be a bit faster with range query precomputation.
    let allStones = 0;
    for (let i = l; i < piles.length; i++) {
      allStones += piles[i];
    }

    // we can take up to the first 2m piles, or if 2m is even bigger than all the piles, up to the last pile
    for (let i = l; i <= Math.min(l + 2 * m - 1, piles.length - 1); i++) {
      const pilesTaken = i - l + 1;
      let maxPilesNextPlayerCanTake = Math.max(m, pilesTaken); // either previous max or new max
      maxPilesNextPlayerCanTake = Math.min(
        maxPilesNextPlayerCanTake,
        piles.length - 1 - (i + 1) + 1
      ); // but they can never take more piles than how many are left

      const maxStonesOpponentCanTake = dp(i + 1, maxPilesNextPlayerCanTake);
      const stonesWeGetIfWeTakeThisManyPiles =
        allStones - maxStonesOpponentCanTake;

      maxStonesWeCanGet = Math.max(
        maxStonesWeCanGet,
        stonesWeGetIfWeTakeThisManyPiles
      );
    }

    memo[l][m] = maxStonesWeCanGet;
    return maxStonesWeCanGet;
  }

  return dp(0, 1);
};
