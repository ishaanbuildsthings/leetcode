// https://leetcode.com/problems/minimum-difference-between-highest-and-lowest-of-k-scores/description/
// Difficulty: Easy

// Problem
/*
You are given a 0-indexed integer array nums, where nums[i] represents the score of the ith student. You are also given an integer k.

Pick the scores of any k students from the array so that the difference between the highest and the lowest of the k scores is minimized.
*/

// Solution
// O(n log n) time and O(1) space. Sort the array and use a fixed window to iterate over the array, updating the minimum difference.

const minimumDifference = function (nums, k) {
  nums.sort((a, b) => a - b);

  let l = 0;
  let r = k - 1;
  let minimumDifference = Number.POSITIVE_INFINITY;

  while (r < nums.length) {
    minimumDifference = Math.min(minimumDifference, nums[r] - nums[l]);
    l++;
    r++;
  }

  return minimumDifference;
};
