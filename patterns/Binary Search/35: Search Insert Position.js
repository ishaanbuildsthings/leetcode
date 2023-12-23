// https://leetcode.com/problems/search-insert-position/description/
// Difficulty: Easy
// tags: binary search

// Problem
/*
Given a sorted array of distinct integers and a target value, return the index if the target is found. If not, return the index where it would be if it were inserted in order.
*/

// Solution, O(log n) time and O(1) space. Do a binary search to whittle down to the last possible number. If that number is our target, return the index. If that number is too big, say: [1] and our target is 0, we still return the index because our number would take over that index. If that number is too small (say our target is a 4), we would insert it right after the 1, so return l+1.

var searchInsert = function (nums, target) {
  let l = 0;
  let r = nums.length - 1;
  let m = Math.floor((r + l) / 2);
  while (l < r) {
    m = Math.floor((r + l) / 2);
    if (nums[m] < target) {
      l = m + 1;
    } else if (nums[m] >= target) {
      r = m;
    }
  }
  if (nums[l] === target) {
    return l;
  }

  if (target < nums[l]) {
    return l;
  }

  return l + 1;
};
