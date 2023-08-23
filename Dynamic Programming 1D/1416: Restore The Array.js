// https://leetcode.com/problems/restore-the-array/description/
// Difficulty: Hard
// Tags: Dynamic Programming 1d

// Problem
/*
A program was supposed to print an array of integers. The program forgot to print whitespaces and the array is printed as a string of digits s and all we know is that all integers in the array were in the range [1, k] and there are no leading zeros in the array.

Given the string s and the integer k, return the number of the possible arrays that can be printed as s using the mentioned program. Since the answer may be very large, return it modulo 109 + 7.
*/

// Solution, O(n * log k) time, O(n) space
/*
DP over each index, and for each index iterate over up to log k indicies. Standard DP.
*/

const MOD = 10 ** 9 + 7;
var numberOfArrays = function (s, k) {
  // memo[l] gives the answer to the [l:] subproblem
  const memo = new Array(s.length).fill(-1);

  function dp(l) {
    // base case
    if (l === s.length) {
      return 1;
    }

    if (memo[l] !== -1) {
      return memo[l];
    }

    let waysForThis = 0;

    let currentNum = 0; // the accumulated number we have seen
    for (let i = l; i < s.length; i++) {
      const newNum = Number(s[i]);
      currentNum *= 10;
      currentNum += newNum;
      // can only use numbers up to a threshold
      if (currentNum > k) {
        break;
      }

      // we can use the future dp if it doesn't start with a 0
      if (s[i + 1] !== "0") {
        waysForThis += dp(i + 1);
        waysForThis = waysForThis % MOD;
      }
    }

    memo[l] = waysForThis;
    return waysForThis;
  }

  return dp(0);
};
