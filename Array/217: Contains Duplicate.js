// https://leetcode.com/problems/contains-duplicate/
// Difficulty: Easy

// Solution
// O(n) time and space, iterates and adds to a set

const containsDuplicate = function (nums) {
  const hashSet = new Set();
  for (const num of nums) {
    if (hashSet.has(num)) return true;
    hashSet.add(num);
  }
  return false;
};
