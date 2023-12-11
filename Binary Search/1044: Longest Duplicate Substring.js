// https://leetcode.com/problems/longest-duplicate-substring/editorial/
// Difficulty: Hard
// tags: binary search, rolling hash

// Problem
/*
Given a string s, consider all duplicated substrings: (contiguous) substrings of s that occur 2 or more times. The occurrences may overlap.

Return any duplicated substring that has the longest possible length. If s does not have a duplicated substring, the answer is "".

Input: s = "banana"
Output: "ana"
*/

// Solution O(n log n) time if few collisions, and O(n) space
/*
Do a binary search to determine the longest possible substring (log n). For each of these operations, do n rolling hashes, and every time we get a collision do a naive check. n log n time for this. If we have collisions all the time, we have end up doing nK operations where K is the length of the window, so nK log n.
*/

var longestDupSubstring = function (s) {
  let longestString = ""; // the final return value, updates every time we find a match

  const arr = s.split("").map((letter) => letter.charCodeAt(0) - 96);
  // bounds for binary search
  let l = 0;
  let r = s.length;
  let m = Math.floor((r + l) / 2);
  while (l <= r) {
    // try a size for this rolling hash
    m = Math.floor((r + l) / 2);
    if (m === 0) {
      return "";
    }
    const [duplicateFound, duplicateString] = rollingHash(arr, m, s);
    if (duplicateFound) {
      l = m + 1;
      if (duplicateString.length > longestString.length)
        longestString = duplicateString;
    } else {
      r = m - 1;
    }
  }
  return longestString;
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
    current = (current * base) % MOD;
    cache[i] = current;
  }
  return current;
}

//computes hashes for a given size, then checks if there are duplicates
function rollingHash(arr, length, s) {
  let result = false; // returns true if a match was found of the given size
  let returnString; // the substring itself we will return if we found a match

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
    currentHash = (currentHash - lostContribution) % MOD;
    if (currentHash < 0) currentHash += MOD;
    currentHash = (currentHash * BASE) % MOD; // shift bits up
    const newNumber = arr[left + length - 1];
    currentHash = (currentHash + newNumber) % MOD;
    if (currentHash in hashes) {
      // we found a duplicate hash
      for (const coords of hashes[currentHash]) {
        const substring = s.slice(coords[0], coords[1] + 1);
        const currentSubstring = s.slice(left, left + length);
        if (substring === currentSubstring) {
          result = true;
          returnString = substring;
          return [result, returnString];
        }
      }
      hashes[currentHash].push([left, left + length - 1]);
    } else {
      hashes[currentHash] = [[left, left + length - 1]];
    }
  }
  return [result, returnString];
}
