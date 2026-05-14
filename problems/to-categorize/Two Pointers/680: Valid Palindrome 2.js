// https://leetcode.com/problems/valid-palindrome-ii/description/
// Difficulty: Easy
// tags: two pointers, palindrome

// Solution
// O(n) time and O(1) space. Use two pointers to iterate over the string from the left and right. If we ever get a mismatched character, try deleting both options and check if either of those form palindrones. Use a helper function to check the pure palindromes, and don't create a new string with .slice, instead, just pass the string and the relevant pointers to the helper.

const validPalindrome = function (s) {
  let l = 0;
  let r = s.length - 1;
  while (l < r) {
    if (s[l] === s[r]) {
      l++;
      r--;
      continue;
    }
    // if there is a mismatch
    return checkPalindrome(s, l + 1, r) || checkPalindrome(s, l, r - 1);
  }
  // if the string itself is a palindrome
  return true;
};

function checkPalindrome(string, l, r) {
  while (l < r) {
    if (string[l] !== string[r]) {
      return false;
    }
    l++;
    r--;
  }
  return true;
}
