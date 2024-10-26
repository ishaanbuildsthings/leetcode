// https://leetcode.com/problems/frog-jump/description/
// Difficulty: Hard
// Tags: Dynamic Programming 2d

// Problem
/*
A frog is crossing a river. The river is divided into some number of units, and at each unit, there may or may not exist a stone. The frog can jump on a stone, but it must not jump into the water.

Given a list of stones' positions (in units) in sorted ascending order, determine if the frog can cross the river by landing on the last stone. Initially, the frog is on the first stone and assumes the first jump must be 1 unit.

If the frog's last jump was k units, its next jump must be either k - 1, k, or k + 1 units. The frog can only jump in the forward direction.
*/

// Solution, O(n^2) time and O(n^2) space
/*
If a frog makes a jump, it ends up at a stone with 3 possible new jump lengths. We make a dp that's current stone by previous jump size. Since for each stone, we have up to n possible previous jump sizes.
*/

/**
 * @param {number[]} stones
 * @return {boolean}
 */
var canCross = function (stones) {
  // edge case, since our first jump and stone are fixed, we need a second stone at position 1, otherwise the dp we return is invalidated
  if (stones[1] !== 1) {
    return false;
  }

  const positions = {}; // maps a unit distance to its index
  for (let i = 0; i < stones.length; i++) {
    const position = stones[i];
    positions[position] = i;
  }

  // memo[l][lastjumpsize] tells us the answer to that problem
  const memo = new Array(stones.length).fill().map(() => ({}));

  function dp(l, lastJumpSize) {
    // base case, we are at the last stone
    if (l === stones.length - 1) {
      return true;
    }

    if (memo[l][lastJumpSize] !== undefined) {
      return memo[l][lastJumpSize];
    }

    const currentPosition = stones[l];

    let resultForThis = false;

    // if we jump the same size
    if (lastJumpSize !== 0) {
      const newPositionIfSame = currentPosition + lastJumpSize;
      if (positions[newPositionIfSame] !== undefined) {
        const ifJumpSame = dp(positions[newPositionIfSame], lastJumpSize);
        resultForThis = resultForThis || ifJumpSame;
      }
    }

    // if we jump bigger
    const newPositionIfBigger = currentPosition + lastJumpSize + 1;
    if (positions[newPositionIfBigger] !== undefined && !resultForThis) {
      const ifJumpBigger = dp(positions[newPositionIfBigger], lastJumpSize + 1);
      resultForThis = resultForThis || ifJumpBigger;
    }

    // if we jump smaller
    if (lastJumpSize !== 1) {
      const newPositionIfSmaller = currentPosition + lastJumpSize - 1;
      if (positions[newPositionIfSmaller] !== undefined && !resultForThis) {
        const ifJumpSmaller = dp(
          positions[newPositionIfSmaller],
          lastJumpSize - 1
        );
        resultForThis = resultForThis || ifJumpSmaller;
      }
    }

    memo[l][lastJumpSize] = resultForThis;
    return resultForThis;
  }

  return dp(1, 0);
};
