// https://leetcode.com/problems/number-of-sub-arrays-of-size-k-and-average-greater-than-or-equal-to-threshold/description/
// Difficulty: Medium
// tags: sliding window fixed

// Problem
/*
Simplified: return the number of subarrays of a fixed window size that have an average >= to a threshold

Given an array of integers arr and two integers k and threshold, return the number of sub-arrays of size k and average greater than or equal to threshold.
*/

// Solution
// O(n) time and O(1) space. Create a currentSum which tracks the current sum of the fixed sliding window, slide over the window, update the sum, and check if we pass the threshold.

const numOfSubarrays = function (arr, k, threshold) {
  let l = 0;
  let r = k - 1;
  let numberOfValidArrays = 0;
  // initialize dpSum
  let currentSum = 0;
  for (let i = 0; i < k; i++) {
    currentSum += arr[i];
  }

  while (r < arr.length) {
    if (currentSum / k >= threshold) {
      numberOfValidArrays++;
    }
    // move the right pointer over and add number
    r++;
    currentSum += arr[r];
    // remove number from left and move pointer
    currentSum -= arr[l];
    l++;
  }

  return numberOfValidArrays;
};
