// https://leetcode.com/problems/find-pivot-index/description/
// Difficulty: Easy
// tags: prefix / postfix

// Solution
// O(n) time and O(1) space. Maintain a prefix sum and postfix sum. Iterate over the array and check if the prefix sum is equal to the postfix sum. If so, return the index. Otherwise, increment the prefix sum and decrement the postfix sum.

const pivotIndex = function (nums) {
  let prefixSum = 0;
  let postfixSum = nums.reduce((acc, val) => acc + val) - nums[0];
  for (let i = 0; i < nums.length; i++) {
    if (prefixSum === postfixSum) {
      return i;
    }
    prefixSum += nums[i];
    postfixSum -= nums[i + 1];
  }
  return -1;
};
