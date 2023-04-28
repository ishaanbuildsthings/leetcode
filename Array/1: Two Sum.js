// https://leetcode.com/problems/two-sum/
// Difficulty: Easy

// Solution 1
// O(n) time and space. Maps numbers in a dictionary and iterates.

const twoSum = function (nums, target) {
  const dict = {}; // maps numbers to their indices
  for (let i = 0; i < nums.length; i++) {
    if (target - nums[i] in dict) {
      return [i, dict[target - nums[i]]];
    }
    dict[nums[i]] = i;
  }
};

// Solution 2
// O(n^2) time and O(1) space. Checks all pairs of numbers.
