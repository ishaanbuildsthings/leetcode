// https://leetcode.com/problems/find-the-smallest-divisor-given-a-threshold/description/
// difficulty: Medium
// tags: binary search

// Problem
/*
Given an array of integers nums and an integer threshold, we will choose a positive integer divisor, divide all the array by it, and sum the division's result. Find the smallest divisor such that the result mentioned above is less than or equal to threshold.

Each result of the division is rounded to the nearest integer greater than or equal to that element. (For example: 7/3 = 3 and 10/2 = 5).

The test cases are generated so that there will be an answer.
*/

// Solution n * log(max(arr)) time, O(1) space
/*
Since we are trying to minimize the divisor, while keeping under the threshold limit, we can use binary search. The lower left search boundary is 0, and the right is the largest number, since that would give an easiest case for the threshold (every answer adds 1).

For each test, we do an n operation to check.
*/

var smallestDivisor = function (nums, threshold) {
  let l = 0;
  let r = Math.max(...nums); // we can create a lower bound for the top of our binary search at the max of the array, since at that point whenever we divide we always get 1
  while (l < r) {
    const m = Math.floor((r + l) / 2); // m is the divisor we will try
    let runningSum = 0;
    for (const num of nums) {
      runningSum += Math.ceil(num / m);
    }
    // if the sum is too small, or equal, we can try an even smaller number
    if (runningSum <= threshold) {
      r = m;
    } else {
      l = m + 1;
    }
  }
  return r;
};
