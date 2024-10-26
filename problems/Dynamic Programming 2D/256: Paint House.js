// https://leetcode.com/problems/paint-house/description/?envType=study-plan-v2&envId=dynamic-programming
// Difficulty: Medium
// tags: dynamic programming 2d

// Problem
/*
Example:
Input: costs = [[17,2,17],[16,16,5],[14,3,19]]
Output: 10
Explanation: Paint house 0 into blue, paint house 1 into green, paint house 2 into blue.
Minimum cost: 2 + 5 + 3 = 10.

Detailed:
There is a row of n houses, where each house can be painted one of three colors: red, blue, or green. The cost of painting each house with a certain color is different. You have to paint all the houses such that no two adjacent houses have the same color.

The cost of painting each house with a certain color is represented by an n x 3 cost matrix costs.

For example, costs[0][0] is the cost of painting house 0 with the color red; costs[1][2] is the cost of painting house 1 with color green, and so on...
Return the minimum cost to paint all houses.
*/

// Solution, O(n) time and O(1) space. We can do this in place.
/*
For each state, we can paint the house a different color than the previous, and get a new subproblem which is paint the remaining houses given a certain previous color. We memoize these. There are 3*n states and each takes 3 time to solve, so O(n) time and O(n) space.
*/

var minCost = function (costs) {
  const NUM_HOUSES = costs.length;
  const NUM_COLORS = 3;

  // memo[leftHouseIndex][prevColor] represents the minimum cost to paint the [i:] houses where the previous color was `prevColor`
  const memo = new Array(NUM_HOUSES)
    .fill()
    .map(() => new Array(NUM_COLORS).fill(-1));

  memo[0][-1] = -1; // a bit of a hack, since the very first house we paint can be painted any color, I said the previous color used was -1, so that the code tests all colors for the first house. but if I do that, the memoization check triggers, so I hardcode this to -1 so that doesn't trigger

  function dp(leftHouseIndex, prevColorNum) {
    // base case, we painted all houses
    if (leftHouseIndex === NUM_HOUSES) {
      return 0;
    }

    // memo
    if (memo[leftHouseIndex][prevColorNum] !== -1) {
      return memo[leftHouseIndex][prevColorNum];
    }

    let minCost = Infinity;

    // try all colors (except the previous color)
    for (let i = 0; i < NUM_COLORS; i++) {
      if (i === prevColorNum) {
        continue;
      }
      const costToPaintHouseThisColor = costs[leftHouseIndex][i];
      const costIfWeChooseThis =
        costToPaintHouseThisColor + dp(leftHouseIndex + 1, i);

      minCost = Math.min(minCost, costIfWeChooseThis);
    }

    memo[leftHouseIndex][prevColorNum] = minCost;
    return minCost;
  }

  return dp(0, -1); // say the previous color was a non-existent one, so we try all colros for the first house
};
