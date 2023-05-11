// https://leetcode.com/problems/longest-common-prefix/description/
// Difficulty: Easy

// Problem
/*
Write a function to find the longest common prefix string amongst an array of strings.

If there is no common prefix, return an empty string "".
*/

// Solution
// O(n*k) time, where n is the number of words and k is how long they are (upper bounded by 200). O(1) space. Iterate over each letter of the first word, to find the expected letter. The first word will bottleneck the longest prefix so this is okay. Then iterate over every word and check if the expectedLetter matches the letters found in those words.

var longestCommonPrefix = function (strs) {
  let longestPrefix = "";

  // iterate over all the letters of the first word, since at most the longest prefix can be that word
  for (let i = 0; i < strs[0].length; i++) {
    const expectedLetter = strs[0][i];
    // iterate over each word
    for (const word of strs) {
      if (word[i] !== expectedLetter) {
        return longestPrefix;
      }
    }
    longestPrefix += expectedLetter;
  }
  return longestPrefix;
};
