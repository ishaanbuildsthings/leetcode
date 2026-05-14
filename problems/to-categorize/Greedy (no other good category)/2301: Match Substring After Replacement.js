// https://leetcode.com/problems/match-substring-after-replacement/description/
// Difficulty: Hard
// tags: greedy

// Problem
/*
Example:
Input: s = "fool3e7bar", sub = "leet", mappings = [["e","3"],["t","7"],["t","8"]]
Output: true
Explanation: Replace the first 'e' in sub with '3' and 't' in sub with '7'.
Now sub = "l3e7" is a substring of s, so we return true.

Detailed:
You are given two strings s and sub. You are also given a 2D character array mappings where mappings[i] = [oldi, newi] indicates that you may perform the following operation any number of times:

Replace a character oldi of sub with newi.
Each character in sub cannot be replaced more than once.

Return true if it is possible to make sub a substring of s by replacing zero or more characters according to mappings. Otherwise, return false.

A substring is a contiguous non-empty sequence of characters within a string.
*/

// Solution, O(n*k) time, O(mappings) space
/*
Start at the leftmost char of s. If it matches the leftmost char of sub, or it can be replaced into that, do so. If we finish the entire sub, we return true.
*/

var matchReplacement = function (s, sub, mappings) {
  // 'a' : Set('b', '5', 'f') means an a can turn into any of those chars
  const charsInto = {};
  for (const tuple of mappings) {
    const [from, to] = tuple;
    if (!(from in charsInto)) {
      charsInto[from] = new Set(to);
    } else {
      charsInto[from].add(to);
    }
  }

  for (let i = 0; i < s.length; i++) {
    let mismatchFound = false;
    for (let j = 0; j < sub.length; j++) {
      const subChar = sub[j];
      const sChar = s[i + j];

      // don't need to process these
      if (subChar === sChar) {
        continue;
      }

      // if we cannot replace this character with anything, we cannot form the replacement
      if (!(subChar in charsInto)) {
        mismatchFound = true;
        break;
      }

      // if we can replace this letter with letters, but not the one we need, we fail
      if (!charsInto[subChar].has(sChar)) {
        mismatchFound = true;
        break;
      }
    }
    if (!mismatchFound) {
      return true;
    }
  }

  return false;
};
