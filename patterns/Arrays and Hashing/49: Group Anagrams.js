//https:leetcode.com/problems/group-anagrams/description/
// Difficulty: Medium
// tags: bucket sort, counting sort

/*
Given an array of strings strs, group the anagrams together. You can return the answer in any order.

An Anagram is a word or phrase formed by rearranging the letters of a different word or phrase, typically using all the original letters exactly once.
*/

// Solution
// O(n * mlogm) with a normal sort, or O(n*m) time with a bucket/counting sort. and O(n*m) space, since for each word we may need to store the entire word in memory, and the word is m letters
// Create a mapping that maps a sorted word to a list of indices that word can come from: { 'ate' : [0, 1, 3], ... }. Iterate over the mapping and push the words into the output array

const groupAnagrams = function (strs) {
  const output = [];

  // n*k storage, since for each word we may need to store the entire word in memory, and the word is k letters
  const mapping = {}; // maps a sorted word to a list of indices that word can come from: { 'ate' : [0, 1, 3], 'ant' : [2, 4], 'bat' : [5] }

  // populate the mapping, n * (m log m) time with a normal sort, or n * m with a bucket or counting sort
  for (let i = 0; i < strs.length; i++) {
    const word = strs[i];
    const wordArray = word.split("");
    const wordArraySorted = wordArray.sort(); // m log m time, where m is the length of the word
    const wordSorted = wordArraySorted.join("");
    if (wordSorted in mapping) {
      mapping[wordSorted].push(i);
    } else {
      mapping[wordSorted] = [i];
    }
  }

  // iterate over mapping and produce the output
  for (sortedWord in mapping) {
    const outputBox = [];
    for (const index of mapping[sortedWord]) {
      outputBox.push(strs[index]);
    }
    output.push(outputBox);
  }
  return output;
};
