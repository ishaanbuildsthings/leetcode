// https://leetcode.com/problems/ransom-note/description/
// Difficulty: Easy

// Solution
// O(n) time and O(1) space. Create a mapping of all the characters in the magazine, then iterate over the ransom note and decrement the mapping. If the count in the mapping is ever negative, return false.

var canConstruct = function (ransomNote, magazine) {
  const chars = "abcdefghijklmnopqrstuvwxyz";
  const mapping = {};
  for (const char of chars) {
    mapping[char] = 0;
  }
  for (const char of magazine) {
    mapping[char]++;
  }

  for (const char of ransomNote) {
    mapping[char]--;
    if (mapping[char] < 0) {
      return false;
    }
  }

  return true;
};
