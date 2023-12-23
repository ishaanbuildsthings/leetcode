// https://leetcode.com/problems/isomorphic-strings/description/
// Difficulty: Easy

// Problem
/*
Simple: paper can map to title, add can map to odd. egg cannot map to pen. Return if the strings are isomorphic.

Detailed:
Given two strings s and t, determine if they are isomorphic.

Two strings s and t are isomorphic if the characters in s can be replaced to get t.

All occurrences of a character must be replaced with another character while preserving the order of characters. No two characters may map to the same character, but a character may map to itself.
*/

// Solution
/*
O(n) time and O(1) space (bounded by # of ascii chars). Create a mapping from the first string to the second, and a set of used chars. Iterate over the first string. If we have already already mapped a character, verify the mapping holds. If we haven't, check if the character we are mapping to has already been mapped to by another character. If it has, return false. Otherwise, add the mapping and the character to the set of used chars.
*/

var isIsomorphic = function (s, t) {
  const mapping = {}; // maps letters to what they must map to
  const usedChars = new Set();

  for (let i = 0; i < s.length; i++) {
    const char1 = s[i];
    const char2 = t[i];

    if (char1 in mapping) {
      // if we have already mapped p to t, and see a p to l, return false
      if (mapping[char1] !== char2) {
        return false;
      }
    } else {
      // if the letter has already been mapped to by another letter
      if (usedChars.has(char2)) {
        return false;
      }
      mapping[char1] = char2;
      usedChars.add(char2);
    }
  }
  return true;
};
