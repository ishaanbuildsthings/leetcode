// https://leetcode.com/problems/paint-house-ii/description/?envType=study-plan-v2&envId=dynamic-programming
// Difficulty: Hard
// tags: dynamic programming 2d

// Problem
/*
Example:
Input: costs = [[1,5,3],[2,9,4]]
Output: 5
Explanation:
Paint house 0 into color 0, paint house 1 into color 2. Minimum cost: 1 + 4 = 5;
Or paint house 0 into color 2, paint house 1 into color 0. Minimum cost: 3 + 2 = 5.

Detailed:
There are a row of n houses, each house can be painted with one of the k colors. The cost of painting each house with a certain color is different. You have to paint all the houses such that no two adjacent houses have the same color.

The cost of painting each house with a certain color is represented by an n x k cost matrix costs.

For example, costs[0][0] is the cost of painting house 0 with color 0; costs[1][2] is the cost of painting house 1 with color 2, and so on...
Return the minimum cost to paint all houses.
*/

// Solution, O(n*k^2) time and O(n*k) space.
/*
For a given house, we can paint it. For the next house, we can paint it any different color. We memoize the results of: paint starting at this house, with a previous house color. There are n*k states and each takes k time to solve.
*/
var minCostII = function (costs) {
  const NUM_HOUSES = costs.length;
  const NUM_COLORS = costs[0].length;
  // memo[i][j] represents we have to paint the houses from [i:] still, and the previous house was painted color j, and the value is the minimum cost for this subproblem
  const memo = new Array(NUM_HOUSES)
    .fill()
    .map(() => new Array(NUM_COLORS).fill(-1));

  memo[0][-1] = -1; // a bit of a hack, since the very first house we paint can be painted any color, I said the previous color used was -1, so that the code tests all colors for the first house. but if I do that, the memoization check triggers, so I hardcode this to -1 so that doesn't trigger

  function dp(leftHouseIndex, prevColorNum) {
    // base case
    if (leftHouseIndex === NUM_HOUSES) {
      return 0;
    }

    if (memo[leftHouseIndex][prevColorNum] !== -1) {
      return memo[leftHouseIndex][prevColorNum];
    }

    let minCost = Infinity;

    // try painting all possible colors for the next house
    for (let i = 0; i < NUM_COLORS; i++) {
      // we can't use the color we just used
      if (i === prevColorNum) {
        continue;
      }

      const costToPaintHouse = costs[leftHouseIndex][i];
      const totalCostIfWeChooseThisOption =
        costToPaintHouse + dp(leftHouseIndex + 1, i);

      minCost = Math.min(minCost, totalCostIfWeChooseThisOption);
    }

    memo[leftHouseIndex][prevColorNum] = minCost;
    return minCost;
  }

  return dp(0, -1);
};
