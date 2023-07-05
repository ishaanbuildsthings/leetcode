// https://leetcode.com/problems/single-number-ii/description/
// Difficulty: Medium
// tags: bit manipulation

// Problem
/*
Given an integer array nums where every element appears three times except for one, which appears exactly once. Find the single element and return it.

You must implement a solution with a linear runtime complexity and use only constant extra space.
*/

// Solution, O(n) time and O(1) space, bit manipulation
/*
Since each number appears 3 times, except for 1, the number that appears three times adds a given bit three times. And the number that appears once only adds its bit once. If we take the total bits for that position mod 3, only the number that appears once comes through. So for each bit position, we iterate through each number, getting if that bit occurs or not. The total bit appearances mod 3 gives us the true ith bit for the result. We set that onto the result.
*/

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
