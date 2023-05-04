// https://leetcode.com/problems/contains-duplicate/
// Difficulty: Easy
// tags: none

// Solution
// O(n) time and space, iterate over list, add elements to a hash set, and use set to detect if there is a duplicate.

const containsDuplicate = function (nums) {
  const hashSet = new Set();
  for (const num of nums) {
    if (hashSet.has(num)) return true;
    hashSet.add(num);
  }
  return false;
};

// Solution 2
// O(n^2) time and O(1) space, checks all pairs of numbers.
