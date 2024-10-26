// https://leetcode.com/problems/valid-palindrome/description/
// Difficulty: Easy
// tags: two pointers, palindrome

// Solution
// O(n) time and O(1) space. Use two pointers to iterate over the string from the left and right. Parse out non-alphanumeric characters. Then, if the characters are the same, increment/decrement the pointers. If they are different, return false.

const isPalindrome = function (s) {
  // lettersSet contains all lowercase letters
  const ALPHANUMERIC = "abcdefghijklmnopqrstuvwxyz0123456789";
  const alphanumericSet = new Set(ALPHANUMERIC);

  let l = 0;
  let r = s.length - 1;

  while (l < r) {
    const leftAlphaNum = s[l].toLowerCase();
    rightAlphaNum = s[r].toLowerCase();

    // if something isn't an alphanumeric, increment/decrement it
    if (!alphanumericSet.has(leftAlphaNum)) {
      l++;
      continue;
    }
    if (!alphanumericSet.has(rightAlphaNum)) {
      r--;
      continue;
    }

    // we have the same alphanumerics
    if (leftAlphaNum === rightAlphaNum) {
      l++;
      r--;
    }
    // we have alphanumerics that are different
    else {
      return false;
    }
  }
  return true;
};
