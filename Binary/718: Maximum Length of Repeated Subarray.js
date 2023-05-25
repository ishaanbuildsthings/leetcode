// computes (10^x) % C without any int overflow, using mod math
function modPow(exponent) {
  let startingPoint = 1;
  for (let i = 2; i <= exponent + 1; i++) {
    // (1*10) % MOD = ((1 % MOD) * (10 % MOD)) % MOD
    const first = startingPoint % MOD;
    // const second = 10 % MOD;
    const big = (first * 10) % MOD;
    startingPoint = big;
  }
  return startingPoint;
}

const MOD = 10 ** 9 + 7;

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
      hashShort *= 10;
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
      hashLong *= 10;
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
