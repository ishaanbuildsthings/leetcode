// https://leetcode.com/problems/predict-the-winner/description/
// difficulty: Medium
// tags: dynamic programming 2d, prefix

// Problem
/*
You are given an integer array nums. Two players are playing a game with this array: player 1 and player 2.

Player 1 and player 2 take turns, with player 1 starting first. Both players start the game with a score of 0. At each turn, the player takes one of the numbers from either end of the array (i.e., nums[0] or nums[nums.length - 1]) which reduces the size of the array by 1. The player adds the chosen number to their score. The game ends when there are no more elements in the array.

Return true if Player 1 can win the game. If the scores of both players are equal, then player 1 is still the winner, and you should also return true. You may assume that both players are playing optimally.
*/

// Solution, O(n^2) time and O(n^2) space
/*
A typical minimax game. We have n^2 subarray states, where each state maps to the most points a player who goes first can get. If we take the left, we get some points, and we see the points the opponent can get from the remaining region, which is the total sum of the remaining region (precomputed with range query) minus the dp for that subregion. If we can get >= half the points in the entire array, we win.
*/

var PredictTheWinner = function (nums) {
  const prefixSums = [];
  let runningSum = 0;
  for (let i = 0; i < nums.length; i++) {
    runningSum += nums[i];
    prefixSums.push(runningSum);
  }
  prefixSums[-1] = 0; // helps with range query

  function rangeQuery(l, r) {
    return prefixSums[r] - prefixSums[l - 1];
  }

  // memo[l][r] answers the most points someone can get from [l:r]
  const memo = new Array(nums.length)
    .fill()
    .map(() => new Array(nums.length).fill(-1));

  function dp(l, r) {
    // base case, we have 1 number left
    if (l === r) {
      return nums[l];
    }

    if (memo[l][r] !== -1) {
      return memo[l][r];
    }

    // if we take the left, we gain that many points. our opponent gains the most points in the remaining region, and we gain all points they didn't take
    let ifTakeLeftOpponentPoints = dp(l + 1, r);
    const ifTakeLeftRangeQuery = rangeQuery(l + 1, r);
    const ifTakeLeftTotalPoints =
      nums[l] + (ifTakeLeftRangeQuery - ifTakeLeftOpponentPoints);

    let ifTakeRightOpponentPoints = dp(l, r - 1);
    const ifTakeRightRangeQuery = rangeQuery(l, r - 1);
    const ifTakeRightTotalPoints =
      nums[r] + (ifTakeRightRangeQuery - ifTakeRightOpponentPoints);

    memo[l][r] = Math.max(ifTakeLeftTotalPoints, ifTakeRightTotalPoints);
    return Math.max(ifTakeLeftTotalPoints, ifTakeRightTotalPoints);
  }

  const totalPoints = nums.reduce((acc, val) => acc + val, 0);
  const pointsWeGet = dp(0, nums.length - 1);
  if (pointsWeGet >= totalPoints / 2) {
    return true;
  }
  return false;
};
