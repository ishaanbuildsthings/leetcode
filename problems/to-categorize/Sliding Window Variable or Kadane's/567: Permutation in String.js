// https://leetcode.com/problems/permutation-in-string/description/
// Difficulty: Medium
// Tags: sliding window variable

// Problem
/*
Simplified: Input: s1 = "ab", s2 = "eidbaooo"
Output: true
Explanation: s2 contains one permutation of s1 ("ba").

Detailed:
Given two strings s1 and s2, return true if s2 contains a permutation of s1, or false otherwise.

In other words, return true if one of s1's permutations is the substring of s2.
*/

// Solution
// O(n) time and O(1) space. Constant space since there are only 26 letters so the storage is fixed. Create two pointers, expand the window, add a character to our mapping, and compare the mappings, which is O(1) due to 26 letters. If they are equal, return true. If we have too many characters of the new character, shrink from the left until we don't.
// * Solution 2, slightly faster is we maintain a count for the number of characters we have, and the number we need. For instance in aab we need 2 things, 2 a's and 1 b. When we increment into this string: 'baba', we reach a b, which puts us at the exact amount we need, so our have count is 1. We increment into a, but we don't have 2 a's yet. We increment to b, which puts us over our count, so we need to decrement until that count is met again. We decrement the first b, putting us at the count. Now we increment to a, reaching 2 a's, making our have count 2, and solving the problem. Also note whenever we decrement, if we decrement too much of another letter, we need to decrement the have count again.

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
