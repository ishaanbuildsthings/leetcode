// https://leetcode.com/problems/can-make-arithmetic-progression-from-sequence/description/
// Difficulty: Easy

// Problem
/*
A sequence of numbers is called an arithmetic progression if the difference between any two consecutive elements is the same.

Given an array of numbers arr, return true if the array can be rearranged to form an arithmetic progression. Otherwise, return false.
*/

// Solution, O(n log n) time and n or 1 space depending on the sort.
// * Solution 2 O(n) time and O(n) space. Find the min and max, then diff. For instance if our min is 1, max is 10, and length is 4, we expect the numbers 1 4 7 10, so a diff of 3. Iterate over the array again and if we see one of those numbers for the first time, continue. If we see it for the second time, that is bad. If we see an unexpected number, that is bad. We could even do it in O(1) space by modifying the array in place as we know where to expect numbers to be.

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
