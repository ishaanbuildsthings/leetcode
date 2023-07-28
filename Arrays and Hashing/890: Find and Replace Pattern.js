// https://leetcode.com/problems/find-and-replace-pattern/description/
// difficulty: Medium

// Problem
/*
Given a list of strings words and a string pattern, return a list of words[i] that match pattern. You may return the answer in any order.

A word matches the pattern if there exists a permutation of letters p so that after replacing every letter x in the pattern with p(x), we get the desired word.

Recall that a permutation of letters is a bijection from letters to letters: every letter maps to another letter, and no two letters map to the same letter.
*/

// Solution, O(pattern length * words length) time, O(1) space
/*
Maintain a mapping of letters that have been mapped. For each word, compare it against the pattern, if the pattern maps to a different letter return false, or if multiple patterns map to the same letter return false (for that word). Worst case, we check every letter, up to pattern.length, for each word.
*/

var findAndReplacePattern = function (words, pattern) {
  function checkWord(word) {
    if (word.length !== pattern.length) {
      return false;
    }

    const letters = {}; // maps the pattern letters to letters they must be in the word
    const seenWordLetters = new Set(); // helps us avoid cases where multiple pattern letters map to the same word letter

    for (let i = 0; i < pattern.length; i++) {
      // if the pattern char has been mapped before, confirm the word char is the same
      if (pattern[i] in letters) {
        const itWasMappedTo = letters[pattern[i]];
        if (word[i] !== itWasMappedTo) {
          return false;
        }
      }

      // if it hasn't been mapped, map it to the letter
      else {
        // if we already saw the word letter before, we also have an error
        if (seenWordLetters.has(word[i])) {
          return false;
        }
        // add the mapping
        letters[pattern[i]] = word[i];
        seenWordLetters.add(word[i]);
      }
    }

    return true;
  }

  return words.filter((word) => checkWord(word));
};
