// https://leetcode.com/problems/maximum-subarray/
// Difficulty: Medium
// tags: sliding window

// question: why is adding each subarray manually n^3 time? that would be adding n subarrays with left pointers and right pointers

// Solution 1
// O(n) time and O(1) space
// Initialize the maximum possible sum to the first value of the array, since we know that is a guaranteed possible sum. Set the current sum to 0. Iterate over the array. At any point if the current sum drops below 0 by adding a new number, reset the current sum to 0, because we won't consider those prior numbers anymore. Add the current number to the current sum, and check if that sum is bigger than our max sum.

const maxSubArray = function (nums) {
  let maxSum = nums[0];
  let currentSum = 0;
  for (const num of nums) {
    if (currentSum < 0) {
      currentSum = 0;
    }
    currentSum += num;
    maxSum = Math.max(maxSum, currentSum);
  }
  return maxSum;
};
