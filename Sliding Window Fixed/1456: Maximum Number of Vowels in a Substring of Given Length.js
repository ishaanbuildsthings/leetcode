// https://leetcode.com/problems/maximum-number-of-vowels-in-a-substring-of-given-length/description/
// Difficulty: Medium
// tags: sliding window fixed

// Problem
/*
Given a string s and an integer k, return the maximum number of vowel letters in any substring of s with length k.

Vowel letters in English are 'a', 'e', 'i', 'o', and 'u'.
*/

const VOWELS = ["a", "e", "i", "o", "u"]; // Array.includes is faster due to cache locality

var maxVowels = function (s, k) {
  let vowelCount = 0;

  // populate initial window
  for (let i = 0; i < k; i++) {
    if (VOWELS.includes(s[i])) {
      vowelCount++;
    }
  }

  let result = vowelCount;

  let l = 0;
  let r = k - 1;
  // since we increment in the loop, we use -1 so we don't ever exceed s
  while (r < s.length - 1) {
    r++;
    l++;
    const lostLetter = s[l - 1];
    if (VOWELS.includes(lostLetter)) {
      vowelCount--;
    }
    const newLetter = s[r];
    if (VOWELS.includes(newLetter)) {
      vowelCount++;
      result = Math.max(result, vowelCount);
    }
  }

  return result;
};
