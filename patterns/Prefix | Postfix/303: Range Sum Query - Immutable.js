// https://leetcode.com/problems/range-sum-query-immutable/description/
// Difficulty: Easy
// tags: prefix

// Solution
// O(n) time to create the prefix array, O(1) time to query it, O(n) space to store the prefix array, but if we don't need nums anymore we could consider it O(1) space. Iterate over nums and create a prefixArray, representing the current tallied sum, including the current number. When we query a range, say: [1, 2, 3] and we query indices [1,2] inclusive, we take the sum of indices [0,2] inclusve, and the sum of indices [0,0] inclusive, and subtract the latter from the former to get the sum of the range.

var NumArray = function (nums) {
  const prefixArray = []; // prefixes are the sums of all the numbers, inclusive of the current index
  let dpPrefix = 0;
  for (let i = 0; i < nums.length; i++) {
    dpPrefix += nums[i];
    prefixArray[i] = dpPrefix;
  }
  this.prefixArray = prefixArray;
};

/**
 * @param {number} left
 * @param {number} right
 * @return {number}
 */
NumArray.prototype.sumRange = function (left, right) {
  const rightSum = this.prefixArray[right];
  let leftSum;
  if (left === 0) {
    leftSum = 0;
  } else {
    leftSum = this.prefixArray[left - 1];
  }

  return rightSum - leftSum;
};
