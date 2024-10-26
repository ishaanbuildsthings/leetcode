// https://leetcode.com/problems/counting-bits/description/
// Difficulty: easy
// Tags: Bit Manipulation, bottom up dynamic programming

// Problem
/*
Given an integer n, return an array ans of length n + 1 such that for each i (0 <= i <= n), ans[i] is the number of 1's in the binary representation of i.
*/

// Solution 1, O(32n) time and O(1) space. Iterate through each number and count the number of 1s in its binary representation, by bit shifting 32 times.
// * Solution 2, O(n) time and O(n) space, tabulation

function getNumberOfOnes(num) {
  let result = 0;
  while (num > 0) {
    if ((num & 1) === 1) {
      result++;
    }
    num = num >> 1;
  }
  return result;
}
var countBits = function (n) {
  const result = [];
  for (let num = 0; num <= n; num++) {
    result.push(getNumberOfOnes(num));
  }
  return result;
};

// Solution 2, O(n) time and O(n) space, tabulation
// The number of 1 bits in a number, is just 1 plus the number of one bits in the number without the last bit, which is found by taking an offset of the largest power of 2 that fits within that number. For instance in 1011, which is 11, the number of one bits is 1 + (011), and 011 is 3, which is found by taking 11 - largest power of 2.

var countBits = function (n) {
  const dp = []; // maps a number to the number of bits it has
  dp[0] = 0;

  let offset = 1; // initially, when we start iterating from 1, the largest power of two that fits within 1, is 1. Once we reach that largest number in our iteration, we double it. This number lets us know which prior DP to check. We start at 1 because 0 is an edge case

  const result = [0]; // 0 is an edge case, since the prior dp we look at is 0 which makes no sense

  for (let i = 1; i <= n; i++) {
    if (i === offset * 2) {
      offset *= 2;
    }
    const bitsInPriorDp = dp[i - offset];
    const newBits = 1 + bitsInPriorDp;
    dp[i] = newBits;
    result.push(newBits);
  }

  return result;
};
