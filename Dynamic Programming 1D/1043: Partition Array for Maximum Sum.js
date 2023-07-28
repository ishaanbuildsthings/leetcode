// https://leetcode.com/problems/partition-array-for-maximum-sum/description/
// difficulty: Medium
// tags: dynamic programming 1d

// Problem
/*
Given an integer array arr, partition the array into (contiguous) subarrays of length at most k. After partitioning, each subarray has their values changed to become the maximum value of that subarray.

Return the largest sum of the given array after partitioning. Test cases are generated so that the answer fits in a 32-bit integer.
*/

// Solution, O(n*k) time and O(n) space
/*
Create answers to subproblems for [l:]. For each state, try up to k split points, and take the future dp sum.
*/

var maxSumAfterPartitioning = function (arr, k) {
  // memo[l] stores the answer for [l:]
  const memo = new Array(arr.length).fill(-1);

  function dp(l) {
    // base case
    if (l === arr.length) {
      return 0;
    }

    if (memo[l] !== -1) {
      return memo[l];
    }

    let resultForThis = 0;
    let currentBiggest = 0;

    for (let i = 0; i < k; i++) {
      if (l + i >= arr.length) {
        break;
      }

      currentBiggest = Math.max(currentBiggest, arr[l + i]);
      const ifSplitHere = currentBiggest * (i + 1) + dp(l + i + 1);
      resultForThis = Math.max(resultForThis, ifSplitHere);
    }

    memo[l] = resultForThis;
    return resultForThis;
  }

  return dp(0);
};
