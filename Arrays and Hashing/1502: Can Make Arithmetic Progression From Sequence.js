// https://leetcode.com/problems/can-make-arithmetic-progression-from-sequence/description/
// Difficulty: Easy

// Problem
/*
A sequence of numbers is called an arithmetic progression if the difference between any two consecutive elements is the same.

Given an array of numbers arr, return true if the array can be rearranged to form an arithmetic progression. Otherwise, return false.
*/

// Solution, O(n log n) time and n or 1 space depending on the sort.

// Sort, then iterate over checking differences.

var canMakeArithmeticProgression = function (arr) {
  arr.sort((a, b) => a - b);
  let difference;
  for (let i = 0; i < arr.length - 1; i++) {
    if (i === 0) {
      difference = arr[i + 1] - arr[i];
    }
    if (arr[i + 1] - arr[i] !== difference) {
      return false;
    }
  }
  return true;
};
