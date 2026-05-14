// https://leetcode.com/problems/optimal-partition-of-string/description/
// Difficulty: Medimum
// tags: kadane's

// Problem
/*
Given a string s, partition the string into one or more substrings such that the characters in each substring are unique. That is, no letter appears in a single substring more than once.

Return the minimum number of substrings in such a partition.

Note that each character should belong to exactly one substring in a partition.
*/

// Solution, O(n) time and O(1) space, as at most our set holds 26 letters.
/*
Iterate over the string, tracking seen letters. Any time we get a duplicate, we need to make a partition cut. Clear the set and add that letter.
*/

var partitionString = function (s) {
  let cuts = 0;

  let currentSeen = new Set();

  for (let i = 0; i < s.length; i++) {
    const char = s[i];
    if (currentSeen.has(char)) {
      cuts++;
      currentSeen = new Set();
      currentSeen.add(char);
    } else {
      currentSeen.add(char);
    }
  }

  return cuts + 1;
};
