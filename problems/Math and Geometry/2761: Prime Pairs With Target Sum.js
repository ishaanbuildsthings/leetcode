// https://leetcode.com/problems/prime-pairs-with-target-sum/description/
// Difficulty: Medium
// tags: math, two pointers

/*
You are given an integer n. We say that two integers x and y form a prime number pair if:

1 <= x <= y <= n
x + y == n
x and y are prime numbers
Return the 2D sorted list of prime number pairs [xi, yi]. The list should be sorted in increasing order of xi. If there are no prime number pairs at all, return an empty array.

Note: A prime number is a natural number greater than 1 with only two factors, itself and 1.
*/

// Solution, O(sieve) + O(n) time. O(sieve) space.
/*
Create a sieve for primes of 10**6 size, as per the max size of n. It is O(n) time if we skip numbers that are not prime.

For a given n, we can gather all primes within n. Do a 2-pointer two-sum style solution to find all pairs.

The sieve is calculated once and reused.
*/

// stores prime info for numbers [0, 1_000_000]
const primes = new Array(1_000_001).fill(true);

primes[0] = false;
primes[1] = false;

for (let i = 2; i <= 1_000_000; i++) {
  if (!primes[i]) {
    continue;
  }
  for (let j = i * i; j <= 1_000_000; j += i) {
    primes[j] = false;
  }
}

var findPrimePairs = function (n) {
  const primesWithinN = []; // list of primes that are within n
  for (let i = 0; i <= n; i++) {
    if (primes[i]) {
      primesWithinN.push(i);
    }
  }

  const result = [];

  // two pointer 2-sum
  l = 0;
  r = primesWithinN.length - 1;

  while (l <= r) {
    const sum = primesWithinN[l] + primesWithinN[r];
    if (sum === n) {
      result.push([primesWithinN[l], primesWithinN[r]]);
      l++;
    } else if (sum < n) {
      l++;
    } else if (sum > n) {
      r--;
    }
  }

  return result;
};
