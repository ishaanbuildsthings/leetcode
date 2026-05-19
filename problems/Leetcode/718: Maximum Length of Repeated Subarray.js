// https://leetcode.com/problems/maximum-length-of-repeated-subarray/description/
// Difficulty: Medium
// tags: binary search, sliding window fixed, rolling hash, beats 100%

// Solution, O(log(min(n,m)) * (n+m)) time and O(n+m) space
// I wrote 2 solutions, 1 with clean code and function re-use, and one that is more expanded (that also includes naive checks).
/*
This is my first solution ever to beat 100% of solutions! To find the longest length for a shared subarray, we can do a binary search on the length. The bounds of the search range are 0 and the length of the shorter subarray (since the answer can never be larger than that).
At any given length, compute a rolling hash for the two windows, crosscheck the hashes, then to an airtight naive check. It takes n+m time to get the hashes for both n and m, and requires n+m space. If we have a collision, do the naive check which is time k, where k is the length we are checking. In expected runtime we will get log(min(n,m) * (n+m)) assuming few hash collisions. If we find a collision we search an even larger size, if not we check a smaller size. To do a naive check, we can look up the hashkey in an object that maps the hashkey to the relevant coordinates of the subarray.
*/
// * Solution 3- there is also an n*(m+n) solution where we slide the smaller subarray over the larger one. As we slde it, we iterate over the shared portion. As we see matches we increment a count, if we see a mismatch we reset the count. I haven't implemented this to see the finer details, but the rough idea does work.

// Solution 1, clean code and function re-use

const MOD = 10 ** 9 + 7;

var findLength = function (nums1, nums2) {
  let l = 0;
  let r = Math.min(nums1.length, nums2.length);
  while (l <= r) {
    const m = Math.floor((r + l) / 2); // try a size of m
    const nums1Hashes = rollingHash(nums1, m);
    const nums2Hashes = rollingHash(nums2, m);
    let matchFound = false;
    for (const hash of Array.from(nums1Hashes)) {
      if (nums2Hashes.has(hash)) {
        l = m + 1;
        matchFound = true;
        break;
      }
    }
    if (!matchFound) {
      r = m - 1;
    }
  }
  return r;
};

// returns 101^e % MOD, better would be to cache everything
const cache = {};
function modPow(e, base = 101) {
  // fails if we try multiple bases
  if (e in cache) {
    return cache[e];
  }
  let current = 1;
  for (let i = 1; i <= e; i++) {
    // (a * b) % c = ((a % c) * (b % c)) % C
    // (a * 10) % c = ((a % c) * 10) % c
    const left = current % MOD;
    current = (left * base) % MOD;
    cache[i] = current;
  }
  return current;
}

// returns a set of all hashes over an arr with windows of given length
function rollingHash(arr, length) {
  const hashes = new Set();
  const base = 101;
  let currentHash = 0;
  // build initial window
  for (let i = 0; i < length; i++) {
    const power = length - i - 1;
    const number = arr[i];
    const contribution = (number * modPow(power)) % MOD;
    currentHash = (currentHash + contribution) % MOD;
  }
  hashes.add(currentHash);

  // slide over remaining array
  for (let left = 1; left <= arr.length - length; left++) {
    const lostNumber = arr[left - 1];
    const lostNumberPower = modPow(length - 1);
    const lostNumberContribution = (lostNumber * lostNumberPower) % MOD;
    currentHash = currentHash - lostNumberContribution;
    if (currentHash < 0) currentHash += MOD;
    currentHash = (currentHash * base) % MOD;
    currentHash = (currentHash + arr[left + length - 1]) % MOD;
    hashes.add(currentHash);
  }

  return hashes;
}

// Solution 2, more expanded, includes naive checks

const cache2 = {}; // maps exponent to result
// computes 101^exponent % MOD
function modPow(exponent) {
  if (exponent in cache) return cache[exponent];

  let startingPoint = 1;
  for (let i = 2; i <= exponent + 1; i++) {
    // (1*101) % MOD = ((1 % MOD) * (101 % MOD)) % MOD
    const first = startingPoint % MOD;
    const second = 101 % MOD;
    const big = (first * second) % MOD;
    startingPoint = big;
  }
  cache[exponent] = startingPoint;
  return startingPoint;
}
const MOD2 = 10 ** 9 + 7;

var findLength = function (nums1, nums2) {
  let shortArray;
  let longArray;
  if (nums1.length <= nums2.length) {
    shortArray = nums1;
    longArray = nums2;
  } else {
    shortArray = nums2;
    longArray = nums1;
  }

  // l and are are the bounds for the space for finding a size of a subarray to use
  let l = 0;
  let r = shortArray.length;
  let m = Math.floor((r + l) / 2);

  // binary search over the shorter array, to identify the max subarray length we can use
  while (l <= r) {
    m = Math.floor((r + l) / 2); // represents new subarray length we are trying

    // given a subarray length, slide over the short array to find all possible hashes
    const hashes = {}; // maps a hash to the coordinates in the substring

    // get the initial window hash
    let hashShort = 0;
    for (let i = 0; i < m; i++) {
      const number = shortArray[i];
      const power = m - i - 1; // m=3 and i=0, we want power of 2
      const contribution = (number * modPow(power)) % MOD;
      hashShort = (hashShort + contribution) % MOD;
    }
    // 37 for test case 32, line 1 length of 0s
    // slide over the remainder of shortArray
    let lShort = 0;
    let rShort = m - 1; // if m is 3, our window should start at [0, 2]
    while (rShort < shortArray.length) {
      hashes[hashShort] = [lShort, rShort];
      rShort++;
      lShort++;
      // if we reach the end break out
      if (rShort === shortArray.length) {
        break;
      }
      const newNum = shortArray[rShort];
      const oldNum = shortArray[lShort - 1];
      const oldContribution = (oldNum * modPow(m - 1)) % MOD;
      hashShort -= oldContribution;
      if (hashShort < 0) {
        hashShort += MOD;
      }
      hashShort *= 101;
      hashShort = hashShort % MOD;
      hashShort += newNum;
      hashShort = hashShort % MOD;
    }
    /* now we have all hashes of length m from the shorter array, slide over the bigger array and do checks when we get a hash collision */

    // get the initial hash for the big window
    let hashLong = 0;
    for (let i = 0; i < m; i++) {
      const number = longArray[i];
      const power = m - i - 1;
      const contribution = (number * modPow(power)) % MOD;
      hashLong = (hashLong + contribution) % MOD;
    }

    let lLong = 0;
    let rLong = m - 1;
    let matchFound = false;

    // slide over the big array checking for matching hash collisions
    while (rLong < longArray.length) {
      // if we get a hash collision verify there is a match
      if (hashLong in hashes) {
        const shortCoords = hashes[hashLong];
        const longStr = JSON.stringify(longArray.slice(lLong, rLong + 1));
        const shortStr = JSON.stringify(
          shortArray.slice(shortCoords[0], shortCoords[1] + 1)
        );

        // if we found a match, we know we can try even longer arrays
        if (longStr === shortStr) {
          matchFound = true;
          break;
        }
      }

      lLong++;
      rLong++;
      const oldNum = longArray[lLong - 1];
      const oldContribution = (oldNum * modPow(m - 1)) % MOD;
      hashLong -= oldContribution;
      if (hashLong < 0) {
        hashLong += MOD;
      }
      hashLong *= 101;
      hashLong = hashLong % MOD;
      const newNum = longArray[rLong];
      hashLong += newNum;
      hashLong = hashLong % MOD;
    }

    if (matchFound) {
      l = m + 1;
    } else {
      r = m - 1;
    }
  }

  return r;
};
