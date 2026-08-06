// https://leetcode.com/problems/find-peak-element/description/?envType=study-plan-v2&id=top-interview-150
// Difficulty: Medium
// Tags: binary search

// Problem
/*
Simplified:
Input: nums = [1,2,3,1]
Output: 2
Explanation: 3 is a peak element and your function should return the index number 2.

Detailed:
A peak element is an element that is strictly greater than its neighbors.

Given a 0-indexed integer array nums, find a peak element, and return its index. If the array contains multiple peaks, return the index to any of the peaks.

You may imagine that nums[-1] = nums[n] = -∞. In other words, an element is always considered to be strictly greater than a neighbor that is outside the array.

You must write an algorithm that runs in O(log n) time.
*/

// Solution, O(log n) time and O(1) space
/*
Do a binary search, at a given number, say [4, 9, 6], compare m (9) to m+1 (6). If m is bigger, we almost have a peak. There are two possible options, m-1 is bigger than m, and we don't have a peak, or m-1 is smaller, and we do have a peak. If m-1 is bigger than m, the same problem with m-1 occurs, and we can keep moving left. Ultimately if we reach a boundary we have a peak as well, since out of bounds are considered -Infinity. So decide which way to move based on that comparison.
*/

var findPeakElement = function (nums) {
  let l = 0;
  let r = nums.length - 1;
  let m = Math.floor((r + l) / 2);
  while (l < r) {
    let m = Math.floor((r + l) / 2);
    if (nums[m] > nums[m + 1]) {
      r = m;
    } else {
      l = m + 1;
    }
  }
  return l;
};
