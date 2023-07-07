// https://leetcode.com/problems/maximize-the-confusion-of-an-exam/description/
// Difficulty: Medium
// tags: Sliding Window variable, binary search

// Problem
/*
Example:
Input: answerKey = "TTFF", k = 2
Output: 4
Explanation: We can replace both the 'F's with 'T's to make answerKey = "TTTT".
There are four consecutive 'T's.

Detailed:
A teacher is writing a test with n true/false questions, with 'T' denoting true and 'F' denoting false. He wants to confuse the students by maximizing the number of consecutive questions with the same answer (multiple trues or multiple falses in a row).

You are given a string answerKey, where answerKey[i] is the original answer to the ith question. In addition, you are given an integer k, the maximum number of times you may perform the following operation:

Change the answer key for any question to 'T' or 'F' (i.e., set answerKey[i] to 'T' or 'F').
Return the maximum number of consecutive 'T's or 'F's in the answer key after performing the operation at most k times.
*/

// Solution, O(n) time and O(1) space
/*
Track how many Ts and Fs we have. We can always make the window valid if we flip all of the least common amount. Normal variable sliding window.

We could also do a binary search for window sizes then do fixed sliding windows, for n log n time.

I also think DP can solve this problem but it is much slower.
*/

var maxConsecutiveAnswers = function (answerKey, k) {
  let l = 0;
  let r = 0;
  let result = 0;
  const count = [0, 0]; // maps current count of T and F in our window

  while (r < answerKey.length) {
    if (answerKey[r] === "T") {
      count[0]++;
    } else {
      count[1]++;
    }

    // while the number we have the least of is more than K, we cant turn the string into letters in a row, so decrement from there
    while (Math.min(count[0], count[1]) > k) {
      const lostChar = answerKey[l];
      if (lostChar === "T") {
        count[0]--;
      } else {
        count[1]--;
      }
      l++;
    }

    result = Math.max(result, r - l + 1);
    r++;
  }

  return result;
};
