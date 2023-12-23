// https://leetcode.com/problems/repeated-substring-pattern/description/
// Difficulty: Easy
// tags: math

// Problem
/*
Given a string s, check if it can be constructed by taking a substring of it and appending multiple copies of the substring together.
*/

// Solution, O(n root n) time, O(n) space for the slice
/*
For a given length of string, find its factors in root n time. For each factor, test if it can be that one repeated.
*/

/**
 * @param {string} s
 * @return {boolean}
 */
var repeatedSubstringPattern = function (s) {
  function getFactors(n) {
    const factors = new Set();
    for (let factor = 1; factor <= Math.floor(Math.sqrt(n)); factor++) {
      if (n % factor === 0) {
        factors.add(factor);
        factors.add(n / factor);
      }
    }
    factors.delete(n); // only allowed to repeat multiple substrings
    return Array.from(factors);
  }

  const factors = getFactors(s.length);
  for (const size of factors) {
    const anchorString = s.slice(0, size);
    let mismatchFound = false;
    for (
      let startingIndex = 0;
      startingIndex <= s.length - size;
      startingIndex += size
    ) {
      const substring = s.slice(startingIndex, startingIndex + size);
      if (substring !== anchorString) {
        mismatchFound = true;
        break;
      }
    }
    if (!mismatchFound) {
      return true;
    }
  }
  return false;
};
