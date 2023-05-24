// https://leetcode.com/problems/is-subsequence/description/
// Difficulty: Easy
// tags: two pointers

// Solution, O(n) time and O(1) space, n is the length of the longer string
// Maintain two pointers, whenever we find a letter in our target, increment that pointer

var isSubsequence = function (s, t) {
  let sPointer = 0;
  for (let i = 0; i < t.length; i++) {
    const letter = t[i];
    const targetLetter = s[sPointer];
    if (letter === targetLetter) {
      sPointer++;
    }
  }
  if (sPointer === s.length) {
    return true;
  }
  return false;
};
