// https://leetcode.com/problems/longest-repeating-substring/description/
// Difficulty: Medium
// tags: rolling hash, sliding window fixed, binary search

// Problem
/*
Given a string s, return the length of the longest repeating substrings. If no repeating substring exists, return 0.

Input: s = "abbaba"
Output: 2
Explanation: The longest repeating substrings are "ab" and "ba", each of which occurs twice.

Input: s = "aabcaabdaab"
Output: 3
Explanation: The longest repeating substring is "aab", which occurs 3 times.
*/

// Solution, O(n log n) time (expected) and O(n) space for hashes. n^2 log n time with collisions.
/*
Do a binary search to determine longest possible substring (log n). Given a certain length, iterate over the string with a fixed window, computing hashes (n time for all hashes). Technically we have (n-L) sliding windows to check, where L is the length of the window. One might thing a sliding window of size n would therefore take no time, but in theory we still compute the hash for the entire window (though if n=L we can skip it). If we have a collision, do a naive check to verify equivalence. Adjust the binary search as needed.

Without a rolling hash, we would iterate over the substring with a fixed window length, L, then grab that substring and put it in a set. We have to compute n-L sliding windows of length L. You could say we are doing n-L operations which are substring checks. Whereas in the rolling hash, I feel like n operations is more accurate, since we process each element of the array indiivdually / we build the initial window. If we have lots of collisions we are basically doing nK time for each log n operation, where k is the length of the window.
*/
// * Solution 2, I also think you could slide the substring across itself, doing 2n iterations, then for each position count across the shared portion, resetting the count if the characters don't match. Resulting in n^2 time.

var longestRepeatingSubstring = function (s) {
  const arr = s.split("").map((letter) => letter.charCodeAt(0) - 96);
  // bounds for binary search
  let l = 0;
  let r = s.length;
  let m = Math.floor((r + l) / 2);
  while (l <= r) {
    // try a size for this rolling hash
    m = Math.floor((r + l) / 2);
    const arrHashes = rollingHash(arr, m);
    let matchFound = false;

    for (const key in arrHashes) {
      if (arrHashes[key].length > 1) {
        matchFound = true;
        break;
      }
    }

    if (matchFound) {
      l = m + 1;
    } else {
      r = m - 1;
    }
  }
  if (r < 0) return 0;
  return r;
};

const BASE = 26;
const MOD = 10 ** 9 + 7;

const cache = {}; // maps e to results
// calculates 26^e % MOD
function modPow(e, base = BASE) {
  if (e in cache) {
    return cache[e];
  }
  let current = 1;
  for (let i = 1; i <= e; i++) {
    // (a * b) % c =   ((a%c)*(b%c)) % c
    const left = current % MOD;
    const right = base % MOD;
    const big = (left * right) % MOD;
    current = big;
    cache[i] = current;
  }
  return current;
}

// computes a map of hashes to the indices they occur at
function rollingHash(arr, length) {
  const hashes = {}; // maps a hash to the coordinates it occured at

  let currentHash = 0;
  // build initial hash
  for (let i = 0; i < length; i++) {
    const exponent = length - i - 1;
    const number = arr[i];
    const contribution = (number * modPow(exponent)) % MOD;
    currentHash = (currentHash + contribution) % MOD;
  }

  hashes[currentHash] = [[0, length - 1]];

  const maxExponent = length - 1;
  // slide over remaining array
  for (let left = 1; left <= arr.length - length; left++) {
    const lostNumber = arr[left - 1];
    const lostContribution = (lostNumber * modPow(maxExponent)) % MOD;
    currentHash = currentHash - lostContribution;
    if (currentHash < 0) currentHash += MOD;
    currentHash = (currentHash * BASE) % MOD; // shift bits up
    const newNumber = arr[left + length - 1];
    currentHash = (currentHash + newNumber) % MOD;
    if (currentHash in hashes) {
      hashes[currentHash].push([left, left + length - 1]);
    } else {
      hashes[currentHash] = [[left, left + length - 1]];
    }
  }

  return hashes;
}
