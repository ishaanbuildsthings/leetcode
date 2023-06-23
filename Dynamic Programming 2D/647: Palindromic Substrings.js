// https://leetcode.com/problems/palindromic-substrings/description/
// Difficulty: Medium
// tags: dynamic programming 2d, palindrome

// Problem
/*
Simplified:
Input: s = "aaa"
Output: 6
Explanation: Six palindromic strings: "a", "a", "a", "aa", "aa", "aaa".

Detailed:
Given a string s, return the number of palindromic substrings in it.

A string is a palindrome when it reads the same backward as forward.

A substring is a contiguous sequence of characters within the string.
*/

// Solution 1, O(n^2) time and O(n^2) space, dynamic programming
// * Solution 2 below is O(n^2) time and O(1) space using expand around centers

/*
Allocate a dp matrix where the dimensions are starting index x ending index. The result of that cell is if that substring is a palindrome. Then, solve prior dp problems as we do normally.

for instance in aba:

  start at the end, is `a` a palindrome, yes, by default all length 1 things are palindromes, this is our base case

  look at b, iterate through all future letters. we see the next letter, a, since the letters are adjacent, they are only a palindrome if the letters are the same, in this case they are not, so `ba` which is [1][2] is not a palindrome

  look at the first a, iterate through the right, `ab` is not a palindrome. but when we get to `aba`, we look at the [1][1] case, and see it is a palindrome, so aba, or [0][2] is now a palindrome
*/

var countSubstrings = function (s) {
  // the dp is a matrix with dimensions starting index by ending index. the result of that cell is if that is a palindrome
  /*
  for instance in aba:
  start at the end, is `a` a palindrome, yes, by default all length 1 things are palindromes, this is our base case
  look at b, iterate through all future letters. we see the next letter, a, since the letters are adjacent, they are only a palindrome if the letters are the same, in this case they are not, so `ba` which is [1][2] is not a palindrome
  look at the first a, iterate through the right, `ab` is not a palindrome. but when we get to `aba`, we look at the [1][1] case, and see it is a palindrome, so aba, or [0][2] is now a palindrome
  */
  const dp = new Array(s.length)
    .fill()
    .map(() => new Array(s.length).fill(false));
  // all length 1 strings are palindromes
  let result = 0;
  for (let i = 0; i < s.length; i++) {
    dp[i][i] = true;
    result++;
  }
  // iterate from the second to last letter, going backwards
  for (let i = s.length - 2; i >= 0; i--) {
    // for a given letter, iterate through all future letters
    for (let j = i + 1; j < s.length; j++) {
      // if the letters are adjacent, we have a palindrome if they are the same
      if (j === i + 1) {
        if (s[j] === s[i]) {
          result++;
          dp[i][j] = true;
        }
        continue; // nothing in between two adjacent letters, so we don't need to handle that
      }
      // if the inbetween substring is a palindrome, and our letters are the same, we get a new palindrome
      if (dp[i + 1][j - 1] && s[j] === s[i]) {
        result++;
        dp[i][j] = true;
      }
    }
  }
  return result;
};

// Solution 2, O(n^2) time and O(1) space, expand around centers
/*
For each index of the string, we expand left and right around that center. As long as those letters are the same, we get another palindrome. This only does odd palindrome's though, we need to do even ones too. I made a helper function to use the starting index and ending index (either the same, or separated by 1, for even palindromes), which then expands around centers and returns the number of palindromes there.
*/

var countSubstrings = function (s) {
  function expandAroundCenters(leftCenter, rightCenter) {
    let palindromesFound;
    // always true for a single letter, but for a two letter case, we return 0 if the letters are different
    if (s[leftCenter] === s[rightCenter]) {
      palindromesFound = 1;
    } else {
      return 0;
    }

    let left = leftCenter - 1;
    let right = rightCenter + 1;

    while (left >= 0 && right < s.length) {
      if (s[left] === s[right]) {
        palindromesFound++;
        left--;
        right++;
      } else {
        break;
      }
    }

    return palindromesFound;
  }

  let result = 0;
  for (let i = 0; i < s.length; i++) {
    result += expandAroundCenters(i, i);
    result += expandAroundCenters(i, i + 1);
  }

  return result;
};
