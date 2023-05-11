// https://leetcode.com/problems/length-of-last-word/description/
// Difficulty: Easy

// Problem

/*
Given a string s consisting of words and spaces, return the length of the last word in the string.
*/

// Solution
// O(n) space and O(1) time. Iterate over the word backwards, identify the first character, then count the word and return the length

var lengthOfLastWord = function (s) {
  let length = 0;

  for (let i = s.length - 1; i >= 0; i--) {
    // we don't care about initial blank spaces
    if (s[i] === " ") {
      continue;
    }

    // we have found the beginning of the word, iterate until another blank space, or until the string ends, and return the length
    while (i >= 0 && s[i] !== " ") {
      length++;
      i--;
    }
    return length;
  }
};
