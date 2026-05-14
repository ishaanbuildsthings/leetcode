// https://leetcode.com/problems/ugly-number/description/
// Difficulty: Easy

// Problem
/*
An ugly number is a positive integer whose prime factors are limited to 2, 3, and 5.

Given an integer n, return true if n is an ugly number.
*/

var isUgly = function (n) {
  // edge case, doesn't prime factorize
  if (n === 0) {
    return false;
  }

  // iterate over the factors, for each one keep dividing until you can't divide anymore, order doesn't matter for prime factorization
  for (let divisor of [2, 3, 5]) {
    while (n % divisor === 0) {
      n /= divisor;
    }
  }

  if (n === 1) {
    return true;
  }
  return false;
};
