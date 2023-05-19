// https://leetcode.com/problems/find-all-numbers-disappeared-in-an-array/description/
// Difficulty: Easy

// Problem
/*
Given an array nums of n integers where nums[i] is in the range [1, n], return an array of all the integers in the range [1, n] that do not appear in nums.
Input: nums = [4,3,2,7,8,2,3,1]
Output: [5,6]
*/

// Solution 1, O(n) time and space

var findDisappearedNumbers = function (nums) {
  const set = new Set();
  for (let i = 0; i < nums.length; i++) {
    set.add(nums[i]);
  }

  const result = [];

  for (let i = 1; i <= nums.length; i++) {
    if (!set.has(i)) {
      result.push(i);
    }
  }

  return result;
};
