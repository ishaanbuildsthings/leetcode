// https://leetcode.com/problems/word-pattern/description/
// Difficulty: Easy

// Problem
/*
Simplified:
Input: pattern = "abba", s = "dog cat cat dog"
Output: true

Detailed:
Given a pattern and a string s, find if s follows the same pattern.

Here follow means a full match, such that there is a bijection between a letter in pattern and a non-empty word in s.
*/

// Solution, O(n) time and O(n) space
/*
Split up the s string into an array of words. Iterate over the words and pattern at the same time. If we have seen a pattern letter for the first time, add that mapping. If it is an old pattern letter, verify if it is the same word. We also need to track the words we have seen, because abba does not match to dog dog dog dog. So if we try to add mapping[b] = 'dog' for the first time, we will have to add it to our seen words set, and we will return false once we see it already exists.
*/

var wordPattern = function (pattern, s) {
  const seenWords = new Set();
  const mapping = {}; // maps letters to words
  const words = s.split(" ");

  if (words.length < pattern.length) {
    return false;
  }

  for (let i = 0; i < words.length; i++) {
    const word = words[i];
    const patternLetter = pattern[i];
    if (patternLetter in mapping) {
      if (mapping[patternLetter] !== word) {
        return false;
      }
    } else {
      if (seenWords.has(word)) {
        return false;
      }
      mapping[patternLetter] = word;
      seenWords.add(word);
    }
  }
  return true;
};
