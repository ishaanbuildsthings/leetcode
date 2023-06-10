// https://leetcode.com/problems/palindrome-partitioning/description/
// Difficulty: Medium
// tags: backtracking

// Problem
/*
Given a string s, partition s such that every
substring
 of the partition is a
palindrome
. Return all possible palindrome partitioning of s.
*/

// Solution

function isPalindrome(str, l, r) {
  while (l < r) {
    if (str[l] !== str[r]) {
      return false;
    }
    l++;
    r--;
  }

  return true;
}

var partition = function (s) {
  const result = [];

  // l and r indicate the two indicies we are currently working with, so in 'aab' if we skip the first a, we now have 'aa' which we could then use
  function backtrack(currentPartitions, l, r, total) {
    if (r === s.length) {
      if (total === s.length) {
        result.push(JSON.parse(JSON.stringify(currentPartitions)));
      }
      return;
    }

    const palindrome = isPalindrome(s, l, r);

    // we choose to use the current substring
    if (palindrome) {
      currentPartitions.push(s.slice(l, r + 1));
      backtrack(currentPartitions, r + 1, r + 1, total + r - l + 1);
      currentPartitions.pop();
    }

    // we choose to skip the current substring
    backtrack(currentPartitions, l, r + 1, total);
  }

  backtrack([], 0, 0, 0);

  return result;
};
