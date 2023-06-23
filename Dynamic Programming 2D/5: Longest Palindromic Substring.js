// https://leetcode.com/problems/longest-palindromic-substring/description/
// Difficulty: Medium
// tags: dynamic programming, 2d, palindrome

// Problem
// Given a string s, return the longest palindromic substring in s.

// Solution 1, O(n^2) time and O(1) space, expand our centers
/*
 * Solution 2, O(n^2) time and O(n^2) space, dynamic programming 2d. Allocate a dp matrix, which stores [startIndex][endIndex] to see if something is a palindrome. For each prior letter, iterate through n future letters, seeing if the outer letters match, and what is inbetween is a palindrome. Similar solution to problem 647: Palindromic Substrings.
 * We could also start at the beginning, at iterate through n prior letters, either left to right or right to left.
 */
// * Solution 3, Manacher's algorithm can do this in linear time.
/*
For each index, start expanding around the centers, checking if the outer letters match, meaning we have a palindrome. Update the result of our longest palindrome (by indices, so we don't do String.slice() each time). Also do this for 2 letter starts, to handle even letter palindromes. Similar to problem 647: Palindromic Substrings.
*/

var longestPalindrome = function (s) {
  // returns the left and right indices of the longest substring we can form starting around the left and right center, if we have an invalid substring of length 2 at the start, it will return crossed indces which would have negative length
  function expandAroundCenters(leftCenter, rightCenter) {
    let left = leftCenter;
    let right = rightCenter;

    // expand around the centers as long as we can
    while (left >= 0 && right < s.length && s[left] === s[right]) {
      left--;
      right++;
    }

    return [left + 1, right - 1];
  }

  let result = [0, 0]; // stores coordinates of the longest substring seen so far
  for (let i = 0; i < s.length; i++) {
    // the leftmost and rightmost indices we get if we start expanding around a single center
    const [leftSingle, rightSingle] = expandAroundCenters(i, i);
    // compare lengths, +1 makes it more clear
    if (rightSingle - leftSingle + 1 > result[1] - result[0] + 1) {
      result[0] = leftSingle;
      result[1] = rightSingle;
    }

    const [leftDouble, rightDouble] = expandAroundCenters(i, i + 1);
    if (rightDouble - leftDouble + 1 > result[1] - result[0] + 1) {
      result[0] = leftDouble;
      result[1] = rightDouble;
    }
  }

  return s.slice(result[0], result[1] + 1);
};
