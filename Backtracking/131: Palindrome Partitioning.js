// https://leetcode.com/problems/palindrome-partitioning/description/
// Difficulty: Medium
// tags: backtracking

// Problem
/*
Given a string s, partition s such that every substring of the partition is a palindrome. Return all possible palindrome partitioning of s.
*/

// Solution
// Depth of tree = # of letters in the string. We can either use that letter to end a palindrome, or keep incrementing, meaning 2 branches. Every time we get a solution, we take n time to serialize it. So time = n * 2^n. Space is O(n) due to the height of the callstack or the size of the array.
/*
Use backtracking. For each letter, we can either end there if it is a palindrome, or keep going. Backtrack on if we do use it as a palindrome, and if we don't. We maintain a total count for the number of letters we have used, so at the end if we skip the last letter we don't count it as a solution.

Another way to implement this without the total letter count is to determine all possible palindromes starting at an index, then backtrack across all of them.
*/

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
