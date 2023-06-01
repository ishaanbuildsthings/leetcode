// https://leetcode.com/problems/fibonacci-number/description/
// Difficulty: Easy
// tags: math, recursion, multibranch (recursive or iterative)

// Problem
/*
The Fibonacci numbers, commonly denoted F(n) form a sequence, called the Fibonacci sequence, such that each number is the sum of the two preceding ones, starting from 0 and 1. That is,

F(0) = 0, F(1) = 1
F(n) = F(n - 1) + F(n - 2), for n > 1.
Given n, calculate F(n).
 */

// Solution 1, basic recursion
// Time: O(2^n) space: O(n)
var fib = function (n) {
  if (n === 0) return 0;
  if (n === 1) return 1;
  return fib(n - 1) + fib(n - 2);
};

// Solution 2, recursion with caching
// Time: O(n) space: O(n)
const cache = {}; // maps n to results, so we do not recompute sub problems. also can be useful for future calls, but would not reduce complexity.
var fib = function (n) {
  if (n === 0) return 0;
  if (n === 1) return 1;
  if (n in cache) return cache[n];

  const result = fib(n - 1) + fib(n - 2);
  cache[n] = result;
  return result;
};

// Solution 3, iterative solution, start at simplest case and go up.
// Time: O(n) space: O(1)

/*
Maintain a left and right variable tracking the two prior numbers. Add them and shift over the variables. Keep going until we reach n.
*/

var fib = function (n) {
  if (n === 0) return 0;
  if (n === 1) return 1;

  let first = 0;
  let second = 1;
  let count = 1; // `right` is the count-th fib number
  while (count < n) {
    const third = first + second;
    first = second;
    second = third;
    count++;
  }

  return second;
};
