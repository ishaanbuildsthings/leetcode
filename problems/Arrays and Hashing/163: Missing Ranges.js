// https://leetcode.com/problems/missing-ranges/description/
// difficulty: easy

// Problem
/*
Simplified:
Input: nums = [0,1,3,50,75], lower = 0, upper = 99
Output: [[2,2],[4,49],[51,74],[76,99]]
Explanation: The ranges are:
[2,2]
[4,49]
[51,74]
[76,99]

Input: nums = [-1], lower = -1, upper = -1
Output: []
Explanation: There are no missing ranges since there are no missing numbers.

Detailed:
You are given an inclusive range [lower, upper] and a sorted unique integer array nums, where all elements are within the inclusive range.

A number x is considered missing if x is in the range [lower, upper] and x is not in nums.

Return the shortest sorted list of ranges that exactly covers all the missing numbers. That is, no element of nums is included in any of the ranges, and each missing number is covered by one of the ranges.
*/

// Solution, O(n) time and O(1) space
/*
Iterate through the range. If we have a number and the next number isn't consecutive, insert a range. We also insert the first range which goes from lower to the first number - 1, and the ending range as well.
*/
var findMissingRanges = function (nums, lower, upper) {
  // edge case
  if (nums.length === 0) {
    return [[lower, upper]];
  }

  const result = [];

  // add the optional first tuple, which goes from the first element to lower
  if (nums[0] > lower) {
    result.push([lower, nums[0] - 1]);
  }

  for (let i = 0; i < nums.length - 1; i++) {
    // if we don't have consecutive numbers
    if (nums[i] + 1 !== nums[i + 1]) {
      result.push([nums[i] + 1, nums[i + 1] - 1]);
    }
  }

  // add the optional last tuple, which goes from the last element to upper
  if (nums[nums.length - 1] < upper) {
    result.push([nums[nums.length - 1] + 1, upper]);
  }

  return result;
};
