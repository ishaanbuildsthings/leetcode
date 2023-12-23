// https://leetcode.com/problems/smallest-even-multiple/description/
// dificulty: easy
// tags: math

// Problem: Given a positive integer n, return the smallest positive integer that is a multiple of both 2 and n.

// Solution, O(1) time and space
var smallestEvenMultiple = function (n) {
  if (n % 2 === 0) return n;
  return n * 2;
};
