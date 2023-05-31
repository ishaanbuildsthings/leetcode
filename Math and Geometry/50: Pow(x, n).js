// https://leetcode.com/problems/powx-n/description/
// Difficulty: Medium
// tags: binary (sort of)

// Problem
// Implement pow(x, n), which calculates x raised to the power n (i.e., xn).

// Solution
// The time complexity is O(log n) because for a power of 100, we do a 50 computation, a 25, a 12, etc, down to a 1. The space complexity is O(log n) because we have a call stack of size log n.
/*
The problem with trying to do 2^1000 is we do a lot of operations, 2*2*2...*2. We could split this up into 2^500 * 2. If we compute 2^500 once, we can cache the value and use that. The function maintains a memoized cache and recursively calls down until the base case, when the power is 1. For negative powers, we just return 1 / x^n.
*/

const cache = {};

// helper function, computes x**n where n is >= 1
function power(x, n) {
  const key = JSON.stringify([x, n]);
  if (key in cache) {
    return cache[key];
  }
  if (n === 1) {
    const result = x;
    cache[key] = result;
    return result;
  }
  // if the power is even, say 2^10, we can do 2^5 * 2^5, compute the
  else if (n % 2 === 0) {
    const result = power(x, n / 2) * power(x, n / 2);
    cache[key] = result;
    return result;
  }
  // if the power is odd, say 2^11, we can do 2^5 * 2^6
  else {
    const result = power(x, Math.floor(n / 2)) * power(x, Math.ceil(n / 2));
    cache[key] = result;
    return result;
  }
}

// main function, handles negative powers
var myPow = function (x, n) {
  if (n === 0) {
    return 1;
  } else if (n > 0) {
    return power(x, n);
  } else {
    return 1 / power(x, Math.abs(n));
  }
};
