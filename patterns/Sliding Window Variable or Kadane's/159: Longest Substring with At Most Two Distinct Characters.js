// https://leetcode.com/problems/longest-substring-with-at-most-two-distinct-characters/description/

// Difficulty: Medium
// Tags: Sliding Window Variable

// Problem
/*
Given a string s, return the length of the longest substring that contains at most two distinct characters.
 */

// Solution, O(n) time and O(1) space
/*
Just iterate, tracking our unique char counts. Update result as needed.
 */
var lengthOfLongestSubstringTwoDistinct = function (s) {
  const counts = {};
  for (const char of "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLNNOPQRSTUVWXYZ") {
    counts[char] = 0;
  }

  let result = 0;

  let l = 0;
  let r = 0;
  let size = 0; // how many unique chars we have
  while (r < s.length) {
    const newChar = s[r];
    counts[newChar]++;
    if (counts[newChar] === 1) {
      size++;
    }

    while (size > 2) {
      const lostChar = s[l];
      counts[lostChar]--;
      if (counts[lostChar] === 0) {
        size--;
      }
      l++;
    }

    const windowLength = r - l + 1;
    result = Math.max(result, windowLength);

    r++;
  }

  return result;
};
