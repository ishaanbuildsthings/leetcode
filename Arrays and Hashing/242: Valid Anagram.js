// https://leetcode.com/problems/valid-anagram/description/
// Difficulty: Easy

// Solution
// O(n) time and O(1) space, since a mapping of letters to ints is constant. Iterate over the first list and increment the mapping, iterate over the second and decrement it. if we ever drop below 0, return false, we don't have to worry about having extra letters from s because we checked the lengths of the arrays are the same already.

const isAnagram = function (s, t) {
  // ensures the strings are the same length passed  this for loop
  if (s.length !== t.length) {
    return false;
  }

  // create mapping
  const LETTERS = "abcdefghijklmonpqrstuvwyxz";
  const occurences = {};
  for (const letter of LETTERS) {
    occurences[letter] = 0;
  }

  // add letters
  for (const letter of s) {
    occurences[letter]++;
  }

  // remove letters, if we ever drop below 0, return false, we don't have to worry about having extra letters from s because we checked the lengths already
  for (const letter of t) {
    if (occurences[letter] === 0) {
      return false;
    }
    occurences[letter]--;
  }

  return true;
};
