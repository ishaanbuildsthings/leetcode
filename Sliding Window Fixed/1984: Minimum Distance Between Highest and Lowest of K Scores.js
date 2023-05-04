// https://leetcode.com/problems/minimum-difference-between-highest-and-lowest-of-k-scores/description/
// Difficulty: Easy

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
