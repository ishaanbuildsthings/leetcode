// https://leetcode.com/problems/minimum-ascii-delete-sum-for-two-strings/description/
// Difficulty: Medium
// Tags: dynamic programming 2d

// Problem
/*
Example:
Input: s1 = "sea", s2 = "eat"
Output: 231
Explanation: Deleting "s" from "sea" adds the ASCII value of "s" (115) to the sum.
Deleting "t" from "eat" adds 116 to the sum.
At the end, both strings are equal, and 115 + 116 = 231 is the minimum sum possible to achieve this.
Detailed:
Given two strings s1 and s2, return the lowest ASCII sum of deleted characters to make two strings equal.
*/

// Solution O(n*m) time and space
/*
If the starts of the strings are the same, the subproblem is just [p1 + 1:] and [p2 + 1:]. Otherwise, we can either delete the first char of s1, or the first char of s2. We take the minimum of these two options.
*/

var minimumDeleteSum = function (s1, s2) {
  const memo = new Array(s1.length)
    .fill()
    .map(() => new Array(s2.length).fill(-1));

  function dp(p1, p2) {
    // base case, if one of the strings is empty, the cost is just the cost of the remaining string
    if (p1 === s1.length) {
      let totalS2Cost = 0;
      for (let i = p2; i < s2.length; i++) {
        totalS2Cost += s2[i].charCodeAt(0);
      }
      return totalS2Cost;
    }

    if (p2 === s2.length) {
      let totalS1Cost = 0;
      for (let i = p1; i < s1.length; i++) {
        totalS1Cost += s1[i].charCodeAt(0);
      }
      return totalS1Cost;
    }

    if (memo[p1][p2] !== -1) {
      return memo[p1][p2];
    }

    let resultForThis = Infinity;

    if (s1[p1] === s2[p2]) {
      resultForThis = dp(p1 + 1, p2 + 1);
    }

    // if the two chars aren't the same, we can try deleting one, or the other
    else {
      // if we delete the first one
      const s1DeleteCost = s1[p1].charCodeAt(0);
      const ifDeleteFirst = s1DeleteCost + dp(p1 + 1, p2);

      const s2DeleteCost = s2[p2].charCodeAt(0);
      const ifDeleteSecond = s2DeleteCost + dp(p1, p2 + 1);

      resultForThis = Math.min(ifDeleteFirst, ifDeleteSecond);
    }

    memo[p1][p2] = resultForThis;
    return resultForThis;
  }

  return dp(0, 0);
};
