// https://leetcode.com/problems/shortest-way-to-form-string/description/
// difficulty: medium
// tags: subsequence

// Problem
/*
A subsequence of a string is a new string that is formed from the original string by deleting some (can be none) of the characters without disturbing the relative positions of the remaining characters. (i.e., "ace" is a subsequence of "abcde" while "aec" is not).

Given two strings source and target, return the minimum number of subsequences of source such that their concatenation equals target. If the task is impossible, return -1.
*/

// Solution, O(source * target) time, O(1) space
/*
Define a function isSubsequence which takes a subarray (defined by pointers) from target, and determines if it is a subsequence in source, which takes O(source) time. Then, iterate through the target. Greedily accumulate longer subsequences until one isn't valid.
*/

var shortestWay = function (source, target) {
  function isSubsequenceOf(subarrayL, subarrayR) {
    let i = subarrayL;
    for (const char of source) {
      if (char === target[i]) {
        i++;
        if (i === subarrayR + 1) {
          return true;
        }
      }
    }
    return false;
  }

  let l = 0;
  let result = 0;
  for (let i = 0; i < target.length; i++) {
    const leftIndex = l;
    const rightIndex = i;
    if (isSubsequenceOf(leftIndex, rightIndex)) {
      continue;
    } else {
      if (rightIndex === leftIndex) {
        // edge case, there was a single letter that isn't a viable subsequence, this is to prevent infinite looping
        return -1;
      }
      result++;
      l = i;
      i--;
    }
  }

  return result + 1;
};
