// https://leetcode.com/problems/number-of-substrings-with-only-1s/description/
// Difficulty: Medium
// Tags: Sliding Window Variable, Kadane's

// Problem
/*
Given a binary string s, return the number of substrings with all characters 1's. Since the answer may be too large, return it modulo 109 + 7.
*/

// Solution, O(n) time O(1) space, just add triangle numbers as we see 1s

var numSub = function (s) {
  let result = 0;

  let l = 0;
  let r = 0;
  while (r < s.length) {
    if (s[r] === "1") {
      result += r - l + 1;
    } else {
      l = r + 1;
    }
    r++;
  }

  return result % (10 ** 9 + 7);
};
