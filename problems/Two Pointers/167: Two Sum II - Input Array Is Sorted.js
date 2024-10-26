//
// https://leetcode.com/problems/two-sum-ii-input-array-is-sorted/description/
// Difficulty: Medium
// tags: two pointers
// helper: helps 15: 3sum

// Solution
// O(n) time and O(1) space

// Initialize two pointers on the left and right, add their values. If the result is too big, decrement the right pointer to shrink the result, otherwise increment the left one. This works because there is a guaranteed solution.

const twoSum = function (nums, target) {
  let l = 0;
  let r = nums.length - 1;

  while (l < r) {
    const total = nums[l] + nums[r];
    if (total === target) {
      return [l + 1, r + 1];
    } else if (total > target) {
      r--;
    } else if (total < target) {
      l++;
    }
  }
};
