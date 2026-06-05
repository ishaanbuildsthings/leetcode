// https://leetcode.com/problems/maximum-number-of-non-overlapping-palindrome-substrings/description/
// difficulty: Hard
// tags: Dynamic Programming 1d

// Problem
/*
You are given a string s and a positive integer k.

Select a set of non-overlapping substrings from the string s that satisfy the following conditions:

The length of each substring is at least k.
Each substring is a palindrome.
Return the maximum number of substrings in an optimal selection.

A substring is a contiguous sequence of characters within a string.
*/

// Solution, O((n-k)*k) time, O(n) space
/*
First, we must observe that only palindromes of length k or k+1 are useful. If it is length k+2, we might as well use length k due to the greedy nature of the question.

Therefore, to solve it, we can:

1) try a k-length substring at the beginning, plus the dp of a later substring
2) try a k+1 length one, plus the future dp
3) skip the letter

There are some optimizations we can make regarding these. For instance, if the starting k-length substring is a palindrome, we don't have to try k+1. Or if a k length, or k+1 length start was a palindrome, there is no benefit to skipping the letter. For instance abaxxa, we can skip a and b and get axxa, or we can just take aba (not rigorous proof).

Overall, we do n-k iterations, each taking k time.
*/

var maxPalindromes = function (s, k) {
  // memo[l] tells us the maximum amount of non-overlapping palindrome substrings in [l:]
  const memo = new Array(s.length).fill(-1);

  function dp(l) {
    // no letters left
    if (l === s.length) {
      return 0;
    }

    // edge case, helps the later code run cleanly, substrings smaller than k shouldn't be considered
    if (l >= s.length - k + 1) {
      return 0;
    }

    if (memo[l] !== -1) {
      return memo[l];
    }

    let changed = false;

    // if a substring of length k, starting at l, is a palindrome, one option is to take that, along with a subproblem
    let ifKIsPalindrome = 0;
    if (
      s.slice(l, l + k) ===
      s
        .slice(l, l + k)
        .split("")
        .reverse()
        .join("")
    ) {
      changed = true;
      ifKIsPalindrome = 1 + dp(l + k);
    }

    // if a substring of length k + 1 is, we could also try that
    let ifKPlusOneIsPalindrome = 0;
    if (
      s.slice(l, l + k + 1) ===
      s
        .slice(l, l + k + 1)
        .split("")
        .reverse()
        .join("")
    ) {
      changed = true;
      ifKPlusOneIsPalindrome = 1 + dp(l + k + 1);
    }

    // if neither k nor k+1 was a palindrome, we can skip this letter
    if (!changed) {
      ifKIsPalindrome = dp(l + 1); // small hack, just reusing the above variable instead of creating a third one
    }

    const resultForThis = Math.max(ifKIsPalindrome, ifKPlusOneIsPalindrome);
    memo[l] = resultForThis;
    return resultForThis;
  }
  return dp(0);
};
