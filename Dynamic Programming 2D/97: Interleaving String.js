// https://leetcode.com/problems/interleaving-string/description/
// Difficulty: Medium
// tags: dynamic programming 2d, subsequence

// Problem
/*
Example:
s1='ab', s2='cd', s3='acbd'. Output: true, since we can interleave them

Detailed:
Given strings s1, s2, and s3, find whether s3 is formed by an interleaving of s1 and s2.

An interleaving of two strings s and t is a configuration where s and t are divided into n and m
substrings
 respectively, such that:

s = s1 + s2 + ... + sn
t = t1 + t2 + ... + tm
|n - m| <= 1
The interleaving is s1 + t1 + s2 + t2 + s3 + t3 + ... or t1 + s1 + t2 + s2 + t3 + s3 + ...
Note: a + b is the concatenation of strings a and b.
*/

// Solution, O(m*n) time and O(m*n) space.
/*
A common way to break down a large problem is to think, what if we do some action with the first character? So if we are checking if s3 can be made of s1 and s2, see if we assign the first letter of s3 to either s1 or s2 or both depending on what matches. Then, we have a new subproblem.

example: s1 = ab, s2 = ad, s3 = aabd

At the beginning of s3, we know we can solve the problem by checking both:
s1=b, s2=ad, s3=abd
and
s1=ab, s2=d, s3=abd

There are s1*s2 memo cells and each takes a constant amount of time.
*/

var isInterleave = function (s1, s2, s3) {
  // handles edge cases likes s1='' s2='' s3='a'
  if (s1.length + s2.length !== s3.length) {
    return false;
  }
  // memo[i][j] tells us whether we can form whatever is left in s3 based on the indices of the useds characters from s1 and s2
  // so if s1 = 'ab' and s2 'cd' and s3 is acbd and we are at the char 'c' in s3, memo[1][0] would tell us if we can solve this state. I mad the arrays 1 bigger so when we go out of bounds on `i` or `j` our condition of checking the memo is still valid
  const memo = new Array(s1.length + 1)
    .fill()
    .map(() => new Array(s2.length + 1).fill(-1));

  function dp(i, j) {
    if (i === s1.length && j === s2.length) {
      return true;
    }

    if (memo[i][j] !== -1) {
      return memo[i][j];
    }

    const char1 = s1[i];
    const char2 = s2[j];
    const char3 = s3[i + j];

    // if neither character matches, we cannot return anything, so this is the default
    let result = false;

    // if only the string1 char matches, we must use that
    if (char1 === char3 && char2 !== char3) {
      result = dp(i + 1, j);
    }
    // if only string2 char matches
    else if (char2 === char3 && char1 !== char3) {
      result = dp(i, j + 1);
    }
    // if both match
    else if (char1 === char3 && char2 === char3) {
      result = dp(i + 1, j) || dp(i, j + 1);
    }

    memo[i][j] = result;
    return result;
  }

  return dp(0, 0);
};
