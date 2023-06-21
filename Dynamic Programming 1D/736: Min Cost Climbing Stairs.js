// https://leetcode.com/problems/min-cost-climbing-stairs/description/
// Difficulty: Easy
// tags: dynamic programming 1d, bottom up recursion

// Problem
/*
Simplified:
Input: cost = [10,15,20]
Output: 15
Explanation: You will start at index 1.
- Pay 15 and climb two steps to reach the top.
The total cost is 15.

Detailed:
You are given an integer array cost where cost[i] is the cost of ith step on a staircase. Once you pay the cost, you can either climb one or two steps.

You can either start from the step with index 0, or the step with index 1.

Return the minimum cost to reach the top of the floor.
*/

// Solution, O(n) time and O(1) space. Bottom up tabulation but we only need to store 2 prior values.

/*
Start at the 3rd to last step. The minimum to reach the end is the cost of the 3rd to last step, plus the cost of either one step ahead of it, or two ahead. Repeat until the beginning. Since we can either start at step1 or step2, we take the minimum of those.
*/

var minCostClimbingStairs = function (cost) {
  // edge case that lets us iterate from the 3rd to last element later
  if (cost.length === 2) {
    return Math.min(...cost);
  }

  let costRight = cost[cost.length - 1];
  let costLeft = cost[cost.length - 2];
  let currentCost = 0;
  for (let i = cost.length - 3; i >= 0; i--) {
    const option1 = cost[i] + costLeft;
    const option2 = cost[i] + costRight;
    currentCost = Math.min(option1, option2);
    costRight = costLeft;
    costLeft = currentCost;
  }

  return Math.min(currentCost, costRight); // since we can start at the first or second step
};
