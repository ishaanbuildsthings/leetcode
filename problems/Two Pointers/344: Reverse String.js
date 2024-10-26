// https://leetcode.com/problems/reverse-string/description/
// Difficulty: Easy

// Solution
// O(n) time and O(1) space. Create two pointers, iterate over the string and reverse each character of the string.
// note from futre ishaan: this is wrong since it is immutable lol

const reverseString = function (s) {
  let l = 0;
  let r = s.length - 1;
  while (l < r) {
    const temp = s[l];
    s[l] = s[r];
    s[r] = temp;
    l++;
    r--;
  }
  return s;
};
