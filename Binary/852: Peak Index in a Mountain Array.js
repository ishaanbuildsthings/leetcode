// https://leetcode.com/problems/peak-index-in-a-mountain-array/description/
// Difficulty: Medium
// Tags: binary search

// Problem
/*
An array arr a mountain if the following properties hold:

arr.length >= 3
There exists some i with 0 < i < arr.length - 1 such that:
arr[0] < arr[1] < ... < arr[i - 1] < arr[i]
arr[i] > arr[i + 1] > ... > arr[arr.length - 1]
Given a mountain array arr, return the index i such that arr[0] < arr[1] < ... < arr[i - 1] < arr[i] > arr[i + 1] > ... > arr[arr.length - 1].

You must solve it in O(log(arr.length)) time complexity.
*/

// Solution, O(log n) time, O(1) space
/*
Binary search for the first element where the right number is smaller.
*/

var peakIndexInMountainArray = function (arr) {
  let l = 0;
  let r = arr.length - 1;
  // find the first ndex where the right is smaller
  while (l < r) {
    const m = Math.floor((r + l) / 2); // m is the index we check
    const num = arr[m];
    // if the right number is smaller, we should look left inclusively
    if (num > arr[m + 1]) {
      r = m;
    } else {
      l = m + 1;
    }
  }

  return r;
};
