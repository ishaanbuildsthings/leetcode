// https://leetcode.com/problems/palindrome-partitioning-iv/description/
// Difficulty: Hard
// Tags: dynamic programming 2d, palindrome

// Problem
/*
Given a string s, return true if it is possible to split the string s into three non-empty palindromic substrings. Otherwise, return false.​​​​​

A string is said to be palindrome if it the same string when reversed.
*/

// Solution, O(n^2) time and O(n^2) space
/*
Originally, I tried creating a solution where I have dp(l, r, n) where n is the number of splits we need to make. For this, we iterate through every index, checking the left and right split. I guess it is n^3 time since there are 3*n^2 states and each state takes O(n) time to compute, but I think in practice something like this solution could work if I memoized substrings that are palindromes, there are some repeated cases and I think we don't actually check all n^2 cases.

I ended up writing a more functional solution.

First, I iterate over every index, checking if the left is a palindrome, and if the right can be split into two. To check if the right can be split into to, I iterate over every index checking if there is a point where the left and right are palindromes. As long as we memoize what is a palindrome, this is n^2 time.
*/

var checkPartitioning = function (s) {
  function canSplitTwo(l) {
    for (let i = l; i < s.length - 1; i++) {
      // leftPortion = [l, i];
      // rightPortion = [i + 1, s.length - 1];
      if (isPalindrome(l, i) && isPalindrome(i + 1, s.length - 1)) {
        return true;
      }
    }

    return false;
  }

  // isPalindromeMemo[l][r] tells us if [l:r] is a palindrome
  const isPalindromeMemo = new Array(s.length)
    .fill()
    .map(() => new Array(s.length).fill(-1));

  function isPalindrome(l, r) {
    // base case, l>r needed for things like 'aa' in the recurrence relationship
    if (l === r || l > r) {
      return true;
    }

    if (isPalindromeMemo[l][r] !== -1) {
      return isPalindromeMemo[l][r];
    }

    let resultForThis = false;

    if (s[l] === s[r]) {
      resultForThis = isPalindrome(l + 1, r - 1);
    }

    isPalindromeMemo[l][r] = resultForThis;
    return resultForThis;
  }

  for (let i = 0; i < s.length - 2; i++) {
    // leftPortion = [0, i];
    // rightPortion = [i + 1, s.length - 1];
    if (isPalindrome(0, i) && canSplitTwo(i + 1)) {
      return true;
    }
  }

  return false;
};
