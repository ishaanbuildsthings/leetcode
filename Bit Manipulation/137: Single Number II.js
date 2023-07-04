// https://leetcode.com/problems/single-number-ii/description/
// Difficulty: Medium
// tags: bit manipulation

// Problem

var singleNumber = function (nums) {
  let result = 0;
  // for every, we are going to compute what that bit should be in the result
  for (let i = 0; i < 32; i++) {
    let totalBitsForThisPosition = 0;
    for (let num of nums) {
      const ithBitOfNum = (num >> i) & 1;
      totalBitsForThisPosition += ithBitOfNum;
    }
    // each number appears 3 times, or 1, if a number appears 3 times, it adds either 0 or 3 to the totalBitsForThisPosition, so when modded by 3, it gets masked. but if it appears 1 time, the bit goes through. this is basically setting the ith bit based on what we found
    result = result | (totalBitsForThisPosition % 3 << i);
  }

  return result;
};
