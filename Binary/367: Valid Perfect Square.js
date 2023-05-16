// https://leetcode.com/problems/valid-perfect-square/
// Difficulty: Easy
// tags: binary search, math

// Problem
/*
Given a positive integer num, return true if num is a perfect square or false otherwise.

A perfect square is an integer that is the square of an integer. In other words, it is the product of some integer with itself.

You must not use any built-in library function, such as sqrt.
*/

// Solution
// O(log n) time and O(1) space
/* Guess a number, check if the square is too big or too small, then adjust to a new binary search. This can be sped up with newton's method. */

var isPerfectSquare = function (num) {
  let l = 0;
  let r = num;
  let m;
  while (l < r) {
    m = Math.floor((r + l) / 2); // errs left
    if (m * m < num) {
      l = m + 1;
    } else {
      r = m;
    }
  }
  if (l * l === num) {
    return true;
  }

  return false;
};
