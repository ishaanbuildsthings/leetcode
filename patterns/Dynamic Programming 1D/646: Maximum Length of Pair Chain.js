// https://leetcode.com/problems/maximum-length-of-pair-chain/description/
// Difficulty: Medium
// Tags: Dynamic Programming 1d, binary search

// Problem
/*
You are given an array of n pairs pairs where pairs[i] = [lefti, righti] and lefti < righti.

A pair p2 = [c, d] follows a pair p1 = [a, b] if b < c. A chain of pairs can be formed in this fashion.

Return the length longest chain which can be formed.

You do not need to use up all the given intervals. You can select pairs in any order.
*/

// Solution, O(n log n) time, O(n) space
/*
We sort the pairs. For each pair, if we take it, solve a future subproblem starting from the next pair we can take (determined via binary search).
*/

/**
 * @param {number[][]} pairs
 * @return {number}
 */
var findLongestChain = function (pairs) {
  console.log(pairs);
  pairs.sort((a, b) => {
    if (a[0] !== b[0]) {
      return a[0] - b[0];
    }
    return a[1] - b[1];
  });

  // memo[l] tells us the answer to [l:]
  const memo = new Array(pairs.length).fill(-1);

  function dp(l) {
    // base case
    if (l === pairs.length) {
      return 0;
    }

    if (memo[l] !== -1) {
      return memo[l];
    }

    // skip the current number
    const ifSkip = dp(l + 1);

    // if we take it, find the earliest next pair we can take
    const largestNumberIfTake = pairs[l][1];
    // find the first element larger than largestNumberIfTake
    let lower = l;
    let higher = pairs.length - 1;
    while (lower <= higher) {
      const m = Math.floor((lower + higher) / 2);
      const pair = pairs[m];
      const num = pair[0];
      if (num > largestNumberIfTake) {
        higher = m - 1;
      } else {
        lower = m + 1;
      }
    }
    const ifTake = 1 + dp(higher + 1);

    const resultForThis = Math.max(ifSkip, ifTake);
    memo[l] = resultForThis;

    return resultForThis;
  }

  return dp(0);
};
