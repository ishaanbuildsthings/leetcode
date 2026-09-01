// https://leetcode.com/problems/partition-string-into-substrings-with-values-at-most-k/description/
// Difficulty: Medium
// Tags: greedy

// Problem
/*
Example:
Input: s = "165462", k = 60
Output: 4
Explanation: We can partition the string into substrings "16", "54", "6", and "2". Each substring has a value less than or equal to k = 60.
It can be shown that we cannot partition the string into less than 4 substrings.

Detailed:
You are given a string s consisting of digits from 1 to 9 and an integer k.

A partition of a string s is called good if:

Each digit of s is part of exactly one substring.
The value of each substring is less than or equal to k.
Return the minimum number of substrings in a good partition of s. If no good partition of s exists, return -1.

Note that:

The value of a string is its result when interpreted as an integer. For example, the value of "123" is 123 and the value of "1" is 1.
A substring is a contiguous sequence of characters within a string.
*/

// Solution, O(n) time and O(1) space
/*
First, I tried a DP solution with subproblems [l:]. But it felt like I should just use a greedy approach, absorbing as many digits I can into a single number. I didn't prove the correctness but it felt right using a few examples.
*/

var minimumPartition = function (s, k) {
  let splits = 0;
  let currentNumber = 0;

  for (let i = 0; i < s.length; i++) {
    currentNumber *= 10;
    currentNumber += Number(s[i]);
    // if the number fits, we keep going, if it doesn't fit, we add a split, and set to that number
    if (currentNumber > k) {
      currentNumber = Number(s[i]);
      splits++;
    }

    // if even the single digit is too big, we also fail, edge case, since otherwise we assume setting to that single digit puts it under the threshold
    if (currentNumber > k) {
      return -1;
    }
  }

  return splits + 1;
};
