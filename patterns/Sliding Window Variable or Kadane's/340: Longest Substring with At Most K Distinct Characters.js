// https://leetcode.com/problems/longest-substring-with-at-most-k-distinct-characters/description/
// Difficulty: Medium
// tags: sliding window variable

// Problem
/*
Given a string s and an integer k, return the length of the longest substring of s that contains at most k distinct characters.
Input: s = "eceba", k = 2
Output: 3
Explanation: The substring is "ece" with length 3.
*/

// Solution, O(n) time and O(1) space, since our mapping holds at most all valid character types
/*
Create a sliding window, when we encounter a new character, increase the size (haveCount) of our mapping. If the size is too large, start decrementing. Then update max length. Even after we decremenet (implying the size is no longer too large), we still verify that the size is not too large, in case k=0 and we aren't allowed any characters at all.
*/

var lengthOfLongestSubstringKDistinct = function (s, k) {
  let l = 0;
  let r = 0;
  const mapping = {};

  let haveCount = 0; // how many unique characters we have
  let maxLength = 0;

  while (r < s.length) {
    const char = s[r];
    if (char in mapping) {
      if (mapping[char] === 0) {
        haveCount++;
      }
      mapping[char]++;
    } else if (!(char in mapping)) {
      mapping[char] = 1;
      haveCount++;
    }

    while (haveCount > k && l < r) {
      l++;
      mapping[s[l - 1]]--;
      // if we decremented away all of a letter type
      if (mapping[s[l - 1]] === 0) {
        haveCount--;
      }
    }

    if (haveCount <= k) {
      maxLength = Math.max(maxLength, r - l + 1);
    }

    r++;
  }
  return maxLength;
};
