// https://leetcode.com/problems/powx-n/description/
// Difficulty: Medium
// tags: binary (sort of), recursion, multibranch (recursive or iterative)

// Problem
// Implement pow(x, n), which calculates x raised to the power n (i.e., xn).

// Solution 1, recursive
// O(log n) time and O(log n) space. Imagine we are computing 2^20. We would do 2^10 * 2^10('cached' via the calculation in memory). 2^10 would be 2^5 * 2^5('cached') etc. So we end up having a call stack and time of log n.
// * Solution 2 is iterative and better memory

// helper function, computes number^exponent by reducing cases, for instance 2^99 is 2^49 * 2^49('cached') * 2
function power(number, exponent) {
  // base cases
  if (exponent === 1) return number;
  if (exponent === 0) return 1;

  // if even exponent, like 2^100
  if (exponent % 2 === 0) {
    // compute 2^50 * 2^50
    const halfExponent = power(number, exponent / 2);
    const result = halfExponent * halfExponent;
    return result;
  }

  // if odd exponent, like 2^99
  const halfExponentDown = power(number, Math.floor(exponent / 2));
  const result = halfExponentDown * halfExponentDown * number;
  return result;
}

// main function, accounts for negative exponents
var myPow = function (number, exponent) {
  if (exponent >= 0) return power(number, exponent);

  return 1 / power(number, Math.abs(exponent));
};

// Solution 2, iterative
// O(log n) time and O(1) space, starts at exponent e and reduces based on exponetial squaring.

// computes base^e iteratively
function power(base, e) {
  if (e === 0) return 1;
  if (e === 1) return base;

  let multiplier = 1;
  let currentBase = base;
  let exponentsLeft = e;
  while (exponentsLeft > 0) {
    /*
     say we have to compute 2^10
     our current multiplier is 1
     the exponent is even, so we can square the base and halve the exponent
     4^5

     the exponent is odd, so we add a 4 onto our multiplier to get back to even
     multplier: 4
     4^4

     exponent is even
     16^2

     exponent is even
     256^1

     exponent is odd, add on a multplier, 256*4=1024

     */
    if (exponentsLeft % 2 === 0) {
      currentBase *= currentBase;
      exponentsLeft /= 2;
    } else {
      multiplier *= currentBase;
      exponentsLeft--;
    }
  }
  return multiplier;
}

var myPow = function (base, e) {
  if (e < 0) {
    return 1 / power(base, Math.abs(e));
  }
  return power(base, e);
};

// Solution 3, bad recursive
// O(log n) time and O(log n) space (sort of). Uses a cache to maintain a map of x^n and a result. For each power, say 2^10, compute 2^5 * 2^5. When the first 2^5 runs, it will be cached at some point, before the second 2^5 runs. However as we make multiple calls to the main function, with different arguments, our cache grows, since the cache doesn't reset per run, making this solution untenable / its true memory usage high.

const cache = {}; // caches x^n to a given result

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
    const result = power(x, n / 2) * power(x, n / 2); // here, the initial power(x, n / 2) is called, and will be cached by the time the second one is
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
