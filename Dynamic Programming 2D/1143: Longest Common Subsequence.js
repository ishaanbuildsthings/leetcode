// https://leetcode.com/problems/longest-common-subsequence/description/
// Difficulty: Medium
// tags: top down recursion, dynamic programming 2d, bottom up recursion, subsequence

// Problem
/*
Simplified:

Input: text1 = "abcde", text2 = "ace"
Output: 3
Explanation: The longest common subsequence is "ace" and its length is 3.

Detailed:
Given two strings text1 and text2, return the length of their longest common subsequence. If there is no common subsequence, return 0.

A subsequence of a string is a new string generated from the original string with some characters (can be none) deleted without changing the relative order of the remaining characters.

For example, "ace" is a subsequence of "abcde".
A common subsequence of two strings is a subsequence that is common to both strings.
*/

// Solution 1, O(n*m) time and O(n*m) space, top down recursion + memoization
// * Solution 2, same thing but bottom up tabulation
/*
Maintain a DP for [starting text1 index][starting text2 index]

We look at the first letters, a, and x. They are different. This means the longest common subsequence is the max from:

'abcde' + 'bc'

or

'bcde' + 'xbc'

This is breaking the problem down into subproblems.

If the letters are the same, say 'abcde' and 'abc'.

Then the answer to that is 1 + the longest subsequence in 'bcde' and 'bc'.
*/

var longestCommonSubsequence = function (text1, text2) {
  // the dp maps a solution for [starting text1 index][starting text2 index]
  const dp = new Array(text1.length)
    .fill()
    .map(() => new Array(text2.length).fill(null));

  function recurse(startingIndexText1, startingIndexText2) {
    // if we get pushed out of bounds, we have no valid shared substring. for instance in 'a' and 'aa', the starting letter is the same. so we return 1 + the match between '' and 'a', which we make a custom case to return 0 for. we could also put the 0s in the dp table.
    if (
      startingIndexText1 === text1.length ||
      startingIndexText2 === text2.length
    ) {
      return 0;
    }

    if (dp[startingIndexText1][startingIndexText2] !== null) {
      return dp[startingIndexText1][startingIndexText2];
    }

    const startingLetter1 = text1[startingIndexText1];
    const startingLetter2 = text2[startingIndexText2];

    // if the letters are the same, reduce the subproblem to the next substrings, 'ab' and 'ac' is 1 + ('b' and 'c')
    if (startingLetter1 === startingLetter2) {
      const result =
        1 + recurse(startingIndexText1 + 1, startingIndexText2 + 1);
      dp[startingIndexText1][startingIndexText2] = result;
      return result;
    }
    /* here, the first letters are different */

    const ifWeIgnoreText1Letter = recurse(
      startingIndexText1 + 1,
      startingIndexText2
    );
    const ifWeIgnoreText2Letter = recurse(
      startingIndexText1,
      startingIndexText2 + 1
    );

    const result = Math.max(ifWeIgnoreText1Letter, ifWeIgnoreText2Letter);
    dp[startingIndexText1][startingIndexText2] = result;
    return result;
  }

  return recurse(0, 0);
};

// Solution 2, bottom up tabulation

var longestCommonSubsequence = function (text1, text2) {
  /*
    The dp table stores the answer to the longest common subsequence for [ending text1 index][ending text2 index]

    Say we have:
    'abcde'
    'xac'

    look at the base cases, which are solving for the strings 'a' and 'x'. their last letters are different, so the longest common subsequence is the answer to [-1][-1], which are the empty strings, so 0.

    Now try to solve for the subproblem 'a' and 'xa', which is [0][1]. the last letters are the same, so the answer is 1 + the answer to [-1][0], resulting in 1.

    If we try to solve for 'ab' and 'xa' which is [1][1], the last letters are different, so the answer is the max of [0][1] and [1][0].
    */

  // stores the solution for [text1 ending index][text2 ending index]
  const dp = new Array(text1.length)
    .fill()
    .map(() => new Array(text2.length).fill(0));

  for (
    let text1EndingIndex = 0;
    text1EndingIndex < text1.length;
    text1EndingIndex++
  ) {
    for (
      let text2EndingIndex = 0;
      text2EndingIndex < text2.length;
      text2EndingIndex++
    ) {
      // if the ending letters are the same, the solution is 1 + the dp of the prior indices
      if (text1[text1EndingIndex] === text2[text2EndingIndex]) {
        // if the ending index of either was a 0, such as in 'b' and 'ab', which compares '' and 'a', the solution is 1
        if (text1EndingIndex === 0 || text2EndingIndex === 0) {
          dp[text1EndingIndex][text2EndingIndex] = 1;
        }
        // otherwise, the solution is 1 + the dp with prior indices
        else {
          dp[text1EndingIndex][text2EndingIndex] =
            1 + dp[text1EndingIndex - 1][text2EndingIndex - 1];
        }
      }

      // if the ending letters are different, we take the dp of two subproblems and take the max of them
      else {
        // exclude the ending letter from the text1 portion
        let option1;
        if (text1EndingIndex === 0) {
          option1 = 0;
        } else {
          option1 = dp[text1EndingIndex - 1][text2EndingIndex];
        }

        let option2;
        if (text2EndingIndex === 0) {
          option2 = 0;
        } else {
          option2 = dp[text1EndingIndex][text2EndingIndex - 1];
        }

        // the answer to our problem is the max of the subproblems
        dp[text1EndingIndex][text2EndingIndex] = Math.max(option1, option2);
      }
    }
  }

  return dp[text1.length - 1][text2.length - 1];
};
