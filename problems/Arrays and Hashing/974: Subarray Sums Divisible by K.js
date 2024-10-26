// https://leetcode.com/problems/subarray-sums-divisible-by-k/description/
// Difficulty: Medium

// Problem
/*
Given an integer array nums and an integer k, return the number of non-empty subarrays that have a sum divisible by k.

A subarray is a contiguous part of an array.
*/

// Solution, O(n) time O(n) space
/*
We can iterate, maintaining a running sum. We also maintain a hashmap of seen remainders and how many times they occur. Whenever we reach a new number, our sum has some remainder. Based on the number of previous remainders, we can deduce an amount of subarrays. Also handle edge cases where our remainder is 0, or negative.
*/

var subarraysDivByK = function (nums, k) {
  const seenRemainders = {}; // maps remainders to how many times they have occured
  let runningSum = 0;
  let result = 0;
  for (let i = 0; i < nums.length; i++) {
    runningSum += nums[i];
    let remainder = runningSum % k;
    // flip negative remainders around, for instace -1, 3 k=2, we need the prior remainder to show as a 1
    if (remainder < 0) {
      remainder += k;
    }
    const priorSameRemainders = seenRemainders[remainder];
    if (priorSameRemainders !== undefined) {
      result += priorSameRemainders;
    }
    if (!(remainder in seenRemainders)) {
      seenRemainders[remainder] = 1;
    } else {
      seenRemainders[remainder]++;
    }

    // edge case, we still add to result
    if (remainder === 0) {
      result++;
    }
  }

  return result;
};
