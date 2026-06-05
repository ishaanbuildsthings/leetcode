// https://leetcode.com/problems/distinct-subsequences/description/
// Difficulty: Hard
// tags: Dynamic Programming 2d, Dynamic Programming 1d, subsequence

// Problem
/*
Example:
Input: s = "rabbbit", t = "rabbit"
Output: 3
Explanation:
As shown below, there are 3 ways you can generate "rabbit" from s.
rabbbit
rabbbit
rabbbit

Given two strings s and t, return the number of distinct subsequences of s which equals t.

The test cases are generated so that the answer fits on a 32-bit signed integer.
*/

// Solution, O(s*t) time and O(s + t) space
/*
Create a matrix cache of s*t size (see further down for linear space solution which was actually my initial though)

For matrix[i][j], this is how many ways we can make the subsequence out of the substring t[:j], ending at that position in s.

For instance:
s='abb'
t='ab'

memo[0] = [1, -1, -1]

For just the substring of t, 'a', we can make that many ending at that index.

memo[1] = [0, 1, 1]

For the substring 'ab', we can make it in two places.

Each place is easily found by iterating through the memo, accumulating the prior character count, and updating the new count. For instance when solving for 'ab', we "pick up" a's along the way, and when we get to a 'b' we know how many subsequences we can make.

We can just overwrite the same array and do a linear space solution which was the first way I thought about and solved the problem.
*/

var numDistinct = function (s, t) {
  /*
    memo[i] stores information for the longest number of subsequences we can make if that letter is the last letter, for a part of the target string

    for instance in s='babgbag', t='bag'

    at first, we try to make the subsequence b, so memo becomes:
    1010100

    then we try to make ba
    1110130

    then bag
    1111135
    */
  const memo = new Array(s.length).fill(-1);

  // seed the memo
  const firstLetter = t[0];
  for (let i = 0; i < s.length; i++) {
    const currentChar = s[i];
    if (currentChar === firstLetter) {
      memo[i] = 1;
    }
  }

  // try to make subsequences of increasing substring length, eventually making subsequencies of t
  // start at 1, meaning we consider the substring of length 2 first
  for (let i = 1; i < t.length; i++) {
    const charWeAreEndingAt = t[i];
    const previousCharInSubsequence = t[i - 1];

    let previousCountsSeen = 0; // so when we get to the char we are ending at, we know how many subsequences we can make there

    // for each longer substring we are making subsequencies out of, iterate over the dp
    for (let j = 0; j < s.length; j++) {
      const currentChar = s[j];
      const countAtThisLetter = memo[j]; // this is just a tmp variable
      if (currentChar === charWeAreEndingAt) {
        memo[j] = previousCountsSeen;
      }
      if (currentChar === previousCharInSubsequence) {
        previousCountsSeen += countAtThisLetter;
      }
    }
  }

  let result = 0;
  const lastChar = t[t.length - 1];
  for (let i = 0; i < s.length; i++) {
    if (s[i] === lastChar) {
      result += memo[i];
    }
  }

  return result;
};
