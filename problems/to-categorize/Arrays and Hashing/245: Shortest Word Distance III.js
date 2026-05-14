// https://leetcode.com/problems/shortest-word-distance-iii/description/
// Difficulty: Medium

// Problem
/*
Given an array of strings wordsDict and two strings that already exist in the array word1 and word2, return the shortest distance between the occurrence of these two words in the list.

Note that word1 and word2 may be the same. It is guaranteed that they represent two individual words in the list.
*/

// Solution, O(n) time, O(1) space
/*
Just iterate through the words, if we see one of the two relevant words, check the previous word we tracked and update the result as needed.
*/

var shortestWordDistance = function (wordsDict, word1, word2) {
  let lastWordInfo = []; // stores word + index

  let result = Infinity;

  for (let i = 0; i < wordsDict.length; i++) {
    if (wordsDict[i] !== word1 && wordsDict[i] !== word2) {
      continue;
    }

    // if we never had a word yet, just add the info
    if (lastWordInfo.length === 0) {
      lastWordInfo.push(wordsDict[i]);
      lastWordInfo.push(i);
    } else {
      // if our new word is the same as the previous one, update the index
      if (wordsDict[i] === lastWordInfo[0]) {
        // edge case, word1 and word2 are the same
        if (word1 === word2) {
          const distance = i - lastWordInfo[1];
          result = Math.min(result, distance);
        }
        lastWordInfo[1] = i;
      }
      // if the words are different, update the info and result
      else {
        const distance = i - lastWordInfo[1];
        result = Math.min(result, distance);
        lastWordInfo = [wordsDict[i], i];
      }
    }
  }

  return result;
};
