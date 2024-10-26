// https://leetcode.com/problems/unique-length-3-palindromic-subsequences/description/
// Difficulty: Medium
// Tags: palindrome, two pointers

// Solution, O(n) time and O(1) space
/*
Iterate through all letters. For every letter, iterate through the array, finding the left and rightmost position for that letter. After finding these, iterate through the letters in the middle and track them in a set, to determine palindromic subsequences.
*/

const LETTERS = "abcdefghijklmnopqrstuvwxyz";

var countPalindromicSubsequence = function (s) {
  let result = 0;
  for (const letter of LETTERS) {
    let [l, r] = getPointers(letter, s);
    const seenInBetweenLetters = new Set();
    while (l < r) {
      l++;
      if (l === r) {
        break;
      }
      const newLetter = s[l];
      if (!seenInBetweenLetters.has(newLetter)) {
        result++;
        seenInBetweenLetters.add(newLetter);
      }
    }
  }
  return result;
};

// gets the leftmost and rightmost pointers for a given letter
function getPointers(letter, s) {
  let l = 0;
  while (l < s.length) {
    if (s[l] === letter) {
      break;
    }
    l++;
  }

  let r = s.length - 1;
  while (r >= 0) {
    if (s[r] === letter) {
      break;
    }
    r--;
  }

  // failures occur at l=s.length and r=-1

  return [l, r];
}
