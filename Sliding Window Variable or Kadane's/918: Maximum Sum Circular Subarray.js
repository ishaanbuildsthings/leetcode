// https://leetcode.com/problems/maximum-sum-circular-subarray/description/
// Difficulty: Medium
// tags: kadane's, circular

// todo: continue trying 2 pointer / dp solution

// Solution
// O(n) time and O(1) space. Get the maximum contiguous and minimum continguous subarrays. There are two options, our max sum is circular or not circular. If it is circular, it is the value of the entire array minus the smallest contiguous subarray.

const maxSubarraySumCircular = function (nums) {
  let minSum = Number.POSITIVE_INFINITY;
  let maxSum = Number.NEGATIVE_INFINITY;
  let minPrefix = 0; // minimize
  let maxPrefix = 0; // maximize
  for (const num of nums) {
    if (maxPrefix < 0) {
      maxPrefix = 0;
    }
    if (minPrefix > 0) {
      minPrefix = 0;
    }
    maxPrefix += num;
    minPrefix += num;
    maxSum = Math.max(maxPrefix, maxSum);
    minSum = Math.min(minPrefix, minSum);
  }
  const arraySum = nums.reduce((acc, sum) => acc + sum, 0);
  const circularSum = arraySum - minSum;

  // edge case: [-3, -3] our circular sum evaluates to -6 -(-6) = 0, can't have an empty array
  if (circularSum === 0) {
    return maxSum;
  }
  return Math.max(maxSum, circularSum);
};
