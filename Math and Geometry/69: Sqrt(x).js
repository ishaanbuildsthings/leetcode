// https://leetcode.com/problems/sqrtx/description/
// Difficulty: Easy
// tags: binary search

// Problem
/*
Given a non-negative integer x, return the square root of x rounded down to the nearest integer. The returned integer should be non-negative as well.

You must not use any built-in exponent function or operator.

For example, do not use pow(x, 0.5) in c++ or x ** 0.5 in python.
 */

// Solution, O(log n) time and O(1) space. Standard binary search with 0 and n as the bounds of the search space. Newton's method may perform slightly better.

var mySqrt = function (x) {
  let l = 0;
  let r = x;
  while (l <= r) {
    const m = Math.floor((r + l) / 2);
    if (m * m < x) {
      l = m + 1;
    } else if (m * m === x) {
      return m;
    } else if (m * m > x) {
      r = m - 1;
    }
  }
  return r;
};
