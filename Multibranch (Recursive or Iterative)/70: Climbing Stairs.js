// https://leetcode.com/problems/climbing-stairs/description/
// Difficulty: Easy
// tags: math, recursion, multibranch (recursive or iterative)

// Problem
/*
 */

// Solution 1, recursive with caching
// Time: O(n) and space: O(n)

// For any number, compute the prior two numbers. Cache results as needed.

const cache = {}; // maps n to result

var climbStairs = function (n) {
  if (n <= 0) return 0;
  if (n === 1) return 1;
  if (n === 2) return 2;

  if (n in cache) return cache[n];

  const result = climbStairs(n - 1) + climbStairs(n - 2);
  cache[n] = result;

  return result;
};

// Solution 2, iterative
// Time: O(n) and space: O(1)

// Start from the base cases and iterate up until we reach the given number

var climbStairs = function (n) {
  if (n === 1) return 1;
  if (n === 2) return 2;

  let stepsHandled = 2;
  let first = 1; // starts at n=1
  let second = 2; // starts at n=2

  while (stepsHandled < n) {
    const third = first + second;
    first = second;
    second = third;
    stepsHandled++;
  }

  return second;
};
