// https://leetcode.com/problems/split-array-largest-sum/description/
// Difficulty: Hard
// tags: binary search

// Problem
/*
Given an integer array nums and an integer k, split nums into k non-empty subarrays such that the largest sum of any subarray is minimized.

Return the minimized largest sum of the split.

A subarray is a contiguous part of the array.

Example:

Input: nums = [7,2,5,10,8], k = 2
Output: 18
Explanation: There are four ways to split nums into two subarrays.
The best way is to split it into [7,2,5] and [10,8], where the largest sum among the two subarrays is only 18.
*/

// Solution, O(n) + O(log k) time, where n is the length of the array, and k is the sum of the array minus the largest number in the array (binary search space)
/*
  The idea is to minimize the largest sum of any region. We know at most, a region could have sum of all the elements, and at smallest, the region would have a sum of the largest individual element. So do a binary search on those regions. Once we get a sum we want to test, say 10, iterate along the array, maintaining a sum, and any time we would be put over 10, make a cut and reset the sum to that current number. If we make too many cuts, it isn't possible, and allow for a higher sum, or vice versa.
*/

var splitArray = function (nums, k) {
  // l and r represent the lower and higher bounds for possible sums
  let l = Math.max(...nums);
  let r = nums.reduce((acc, val) => acc + val);
  let m = Math.floor((r + l) / 2);
  // what's the smallest possible sum each section will have after splitting the array? it can't be lower than largest value in the array, but it can't be bigger than the sum of the array

  while (l <= r) {
    m = Math.floor((r + l) / 2); // m represents a sum, i.e. we are testing if splitting it into sums of at most m
    let cutsRemaining = k - 1;
    let runningSum = 0;
    for (let i = 0; i < nums.length; i++) {
      if (runningSum + nums[i] > m) {
        cutsRemaining--;
        runningSum = nums[i];
        // if the new single number exceeded our threshold, it can never be done
        if (runningSum > m) {
          cutsRemaining = -1;
          break;
        }
      } else {
        runningSum += nums[i];
      }
    }
    // if we had to make too many partitions for a number, say 17, we should allow sums of 18
    if (cutsRemaining < 0) {
      l = m + 1;
    } else {
      r = m - 1;
    }
  }
  return l;
};
