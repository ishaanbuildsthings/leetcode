// https://leetcode.com/problems/ones-and-zeroes/description/
// Difficulty: Medium
// tags: dynamic programming 2d

// Problem
/*
Example:
Input: strs = ["10","0","1"], m = 1, n = 1
Output: 2
Explanation: The largest subset is {"0", "1"}, so the answer is 2.

Detailed:
You are given an array of binary strings strs and two integers m and n.

Return the size of the largest subset of strs such that there are at most m 0's and n 1's in the subset.

A set x is a subset of a set y if all elements of x are also elements of y.
*/

// Solution, O(length*m*n) time, O(length*m*n) space
/*
For each element, we can either skip it or take it. We memoize the state where we have to consider the remaining [i:] elements, given current 0 and 1 counts.
*/

var findMaxForm = function (strs, m, n) {
  // counts[i] stores a tuple for [0 count, 1 count] for the ith string
  const counts = [];
  for (let i = 0; i < strs.length; i++) {
    let count0 = 0;
    let count1 = 0;
    for (const char of strs[i]) {
      if (char === "0") {
        count0++;
      } else {
        count1++;
      }
    }
    counts[i] = [count0, count1];
  }

  // memo[i][0 count][1 count] holds the answer to that subproblem
  const memo = new Array(strs.length)
    .fill()
    .map(() => new Array(m + 1).fill().map(() => new Array(n + 1).fill(-1)));

  // solves the problem for the remaining strs [i:] given a current 0 and 1 count
  function dp(i, zeroCount, oneCount) {
    // base case, when i is done we cannot add more elements
    if (i === strs.length) {
      return 0;
    }

    if (memo[i][zeroCount][oneCount] !== -1) {
      return memo[i][zeroCount][oneCount];
    }

    let maxCount = -Infinity;
    // we can either take the ith element, or leave it

    // take the ith element, if it fits
    const [ithZeroCount, ithOneCount] = counts[i];
    if (zeroCount + ithZeroCount <= m && oneCount + ithOneCount <= n) {
      maxCount =
        1 + dp(i + 1, zeroCount + ithZeroCount, oneCount + ithOneCount);
    }

    // skip the ith element
    maxCount = Math.max(maxCount, dp(i + 1, zeroCount, oneCount));

    memo[i][zeroCount][oneCount] = maxCount;
    return maxCount;
  }

  return dp(0, 0, 0);
};
