// https://leetcode.com/problems/factorial-generator/description/
// difficulty: easy

// Problem
// Write a generator function that takes an integer n as an argument and returns a generator object which yields the factorial sequence.

// The factorial sequence is defined by the relation n! = n * (n-1) * (n-2) * ... * 2 * 1​​​.

// The factorial of 0 is defined as 1.

// Solution, we create a generator using counters, edge case for n=0

/**
 * @param {number} n
 * @yields {number}
 */
function* factorial(n) {
  // edge case
  if (!n) {
    yield 1;
  }

  let current = 1;
  let nextToMultiply = 2;
  for (let i = 0; i < n; i++) {
    yield current;
    current *= nextToMultiply;
    nextToMultiply++;
  }
}
