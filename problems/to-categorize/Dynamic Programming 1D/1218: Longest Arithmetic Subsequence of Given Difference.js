// https://leetcode.com/problems/longest-arithmetic-subsequence-of-given-difference/description/
// Difficulty: Medium
// Tags: dynamic programming 1d

// Problem
/*
Given an integer array arr and an integer difference, return the length of the longest subsequence in arr which is an arithmetic sequence such that the difference between adjacent elements in the subsequence equals difference.

A subsequence is a sequence that can be derived from arr by deleting some or no elements without changing the order of the remaining elements.
*/

// Solution 1, dp 1d, O(n) time, O(n) space, since at most there can be n different numbers
/*
Start from the right side (though in hindsight we could have started from the left). Iterate, maintaing a dp for the longest sequence we can make for a given number. When we get to a new number, check if the prior one exists in the dp and update it.
*/

var longestSubsequence = function (arr, difference) {
  const bests = {}; // contains numbers on the right of the current number, mapped to the longest subsequence they can make

  let result = 1;

  for (let i = arr.length - 1; i >= 0; i--) {
    const num = arr[i];
    const numAfterDiff = num + difference;
    if (numAfterDiff in bests) {
      const newLength = bests[numAfterDiff] + 1;
      bests[num] = newLength;
      result = Math.max(result, newLength);
    } else {
      bests[num] = 1;
    }
  }

  return result;
};
