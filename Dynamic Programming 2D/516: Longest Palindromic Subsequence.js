// https://leetcode.com/problems/longest-palindromic-subsequence/description/
// Difficulty: Medium
// tags: dynamic programming 2d, subsequence, palindrome, top down recursion

// Problem
/*
Given a string s, find the longest palindromic subsequence's length in s.

A subsequence is a sequence that can be derived from another sequence by deleting some or no elements without changing the order of the remaining elements.
*/

// Solution, O(n^2) or n^3 time and n^2 space. Dynamic programming 2d.
/*
The kind of weird recurrence relationship I used is:

Given a string, we can either include the first letter, or not include it. If we include it, find the rightmost position where it occurs, and add 2 to the new subproblem. So abax, if we include the first a, we add 2 to the subproblem of b.

If we don't include it, we just take l+1, r as the subproblem, so bax.

We have n^2 subarray problems to solve, maybe each subproblem takes n time since we iterate from the right up to n times, to find the rightmost position of a matching letter. However I can't really tell if this is amortized, though it did pass. We can definitely make it n^2 if we precompute rightmost occurences for things in a range though I'm not even sure if that is possible.

A better recurrence relationship is:
If the first and last letter match, add 2 to the inner subproblem. Otherwise take the max of l+1,r (the letter at l is not part of the subequence) and l,r-1 (the letter at l is part of the subsequence).
*/
var longestPalindromeSubseq = function (s) {
  // create a memo of [l][r] which stores the answer for the subproblem string
  const memo = new Array(s.length)
    .fill()
    .map(() => new Array(s.length).fill(-1));

  function dp(l, r) {
    if (l > r) {
      return 0;
    }
    // base case, otherwise when we try to not include the first letter on 'a', we reach out of bounds
    if (l === r) {
      return 1;
    }

    if (memo[l][r] !== -1) {
      return memo[l][r];
    }

    // we can either include the first letter, or not include it, if we don't include it, we reduce the subproblem to the right
    const dontIncludeFirstLetter = dp(l + 1, r);

    let sizeIfWeIncludeFirstLetter = 0;
    // iterate backwards, finding the furthest right occurence of the letter
    // so in cbbacx, if we want to include the first c, we basically add 2 to the bba subproblem
    for (let i = r; i > l; i--) {
      if (s[i] !== s[l]) {
        continue;
      }
      sizeIfWeIncludeFirstLetter = 2 + dp(l + 1, i - 1);
      break; // we only consider the lastmost position
    }

    const longestSize = Math.max(
      dontIncludeFirstLetter,
      sizeIfWeIncludeFirstLetter
    );

    memo[l][r] = longestSize;
    return longestSize;
  }

  return dp(0, s.length - 1);
};
