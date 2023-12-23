// https://leetcode.com/problems/two-sum/
// Difficulty: Easy
// tags: none

// Solution 1
// O(n) time and space. Map numbers in a dictionary and iterate over list to look for target.

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
