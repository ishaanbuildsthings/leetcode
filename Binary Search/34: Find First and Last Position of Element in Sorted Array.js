// https://leetcode.com/problems/find-first-and-last-position-of-element-in-sorted-array/description/
// Difficulty: Medium
// Tags: Binary Search

// Problem
/*
Given an array of integers nums sorted in non-decreasing order, find the starting and ending position of a given target value.

If target is not found in the array, return [-1, -1].

You must write an algorithm with O(log n) runtime complexity.
Input: nums = [5,7,7,8,8,10], target = 8
Output: [3,4]
*/

// Solution: O(log n^2) time, which is O(log n), and O(1) space. Do a binary search to locate the first position of the target, and do a second to locate the last.

var searchRange = function (nums, target) {
  let l = 0;
  let r = nums.length - 1;
  let m = Math.floor((r + l) / 2);

  // look for the first index of our target
  while (l < r) {
    m = Math.floor((r + l) / 2);
    const num = nums[m];

    // if we see our exact target, we can try to find a further left target, but it isn't guaranteed
    if (num === target) {
      r = m;
    }
    // if our number is too small, consider numbers strictly to the right
    else if (num < target) {
      l = m + 1;
    }
    // if our number is too large, we can consider numbers strictly to the left
    else if (num > target) {
      r = m - 1;
    }
  }

  if (nums[l] !== target) {
    return [-1, -1];
  }

  const leftIndex = l;

  l = 0;
  r = nums.length - 1;
  m = Math.floor((r + l) / 2);

  // look for the last index of our target

  while (l < r) {
    m = Math.ceil((r + l) / 2);
    const num = nums[m];

    // if we see our exact target, we can try looking right, but need to include our number still
    if (num === target) {
      l = m;
    }
    // if our number is smaller than the target, we need to look strictly to the right
    if (num < target) {
      l = m + 1;
    }
    // if our number is bigger than the target, we need to look strictly left
    else if (num > target) {
      r = m - 1;
    }
  }

  return [leftIndex, l];
};
