// https://leetcode.com/problems/permutation-in-string/description/
// Difficulty: Medium
// Tags: sliding window variable

// Problem
/*
Given two strings s1 and s2, return true if s2 contains a permutation of s1, or false otherwise.

In other words, return true if one of s1's permutations is the substring of s2.
*/

// Solution
// O(n) time and O(1) space. Constant space since there are only 26 letters so the storage is fixed. Create two pointers, expand the window, add a character to our mapping, and compare the mappings. If they are equal, return true. If we have too many characters of the new character, shrink from the left until we don't.

const LETTERS = "abcdefghijklmnopqrstuvwxyz";
const templateMap = {};
for (const char of LETTERS) {
  templateMap[char] = 0;
}

var checkInclusion = function (s1, s2) {
  // create the s1Map
  const s1Map = { ...templateMap };
  for (const char of s1) {
    s1Map[char]++;
  }

  // create blank s2Map
  let s2Map = { ...templateMap };

  let l = 0;
  let r = 0;
  while (r < s2.length) {
    const char = s2[r];
    s2Map[char]++;

    // check if our window is a perfect permutation
    if (JSON.stringify(s1Map) === JSON.stringify(s2Map)) {
      return true;
    }

    // if we have too many characters, shrink from the left
    if (s2Map[char] > s1Map[char]) {
      while (s2Map[char] > s1Map[char]) {
        s2Map[s2[l]]--;
        l++;
      }
    }
    r++;
  }

  return false;
};
