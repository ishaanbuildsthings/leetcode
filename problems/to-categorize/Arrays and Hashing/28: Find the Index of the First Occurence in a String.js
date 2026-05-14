// https://leetcode.com/problems/find-the-index-of-the-first-occurrence-in-a-string/description/
// Difficulty: Easy
// Tags: rolling hash, sliding window fixed

// Problem
/*
Given two strings needle and haystack, return the index of the first occurrence of needle in haystack, or -1 if needle is not part of haystack.

Input: haystack = "sadbutsad", needle = "sad"
Output: 0
Explanation: "sad" occurs at index 0 and 6.
The first occurrence is at index 0, so we return 0.
*/

// Solution, O(n+k) time on average, or n*K time with collisions. O(n) space.
/*
Compute a hash for the needle. Roll over the haystack computing hashes, and doing naive checks when we get a collision.
*/

const MOD = 10 ** 9 + 7; // restrict the hash size to be under this
const BASE = 26;

function getAZ(char) {
  // converts a-z to 1-26
  return char.charCodeAt(0) - 96;
}

const cache = {}; // maps e to results
// computes base^e % MOD
function modPow(e, base = BASE) {
  if (e in cache) {
    return cache[e];
  }
  let current = 1;
  for (let i = 1; i <= e; i++) {
    current = ((current % MOD) * base) % MOD;
    cache[i] = current;
  }
  return current;
}

var strStr = function (haystack, needle) {
  // avoid edge case as we would try to hash for undefined values
  if (needle.length > haystack.length) {
    return -1;
  }

  // compute needle hash
  let needleHash = 0;
  for (let i = 0; i < needle.length; i++) {
    const exponent = needle.length - i - 1;
    const contribution = (getAZ(needle[i]) * modPow(exponent)) % MOD;
    needleHash = (needleHash + contribution) % MOD;
  }

  // iterate over the haystack looking for the hash, then doing a naive check

  // compute initial haystack hash
  let haystackHash = 0;
  for (let i = 0; i < needle.length; i++) {
    const exponent = needle.length - i - 1;
    const contribution = (getAZ(haystack[i]) * modPow(exponent)) % MOD;
    haystackHash = (haystackHash + contribution) % MOD;
  }
  // check initial hash
  if (haystackHash === needleHash) {
    if (haystack.slice(0, needle.length) === needle) {
      return 0;
    }
  }

  // slide and check
  const maxExponent = needle.length - 1;
  for (let left = 1; left <= haystack.length - needle.length; left++) {
    const oldNum = getAZ(haystack[left - 1]);
    const oldContribution = (oldNum * modPow(maxExponent)) % MOD;
    haystackHash -= oldContribution;
    if (haystackHash < 0) {
      haystackHash += MOD;
    }
    haystackHash = (haystackHash * BASE) % MOD;
    const newNum = getAZ(haystack[left + needle.length - 1]);
    haystackHash = (haystackHash + newNum) % MOD;
    // if we have a match do a naive check
    // check initial hash
    if (haystackHash === needleHash) {
      if (haystack.slice(left, needle.length + left) === needle) {
        return left;
      }
    }
  }

  return -1;
};

// needle=sasad

// haystack=sasas
//              ^
