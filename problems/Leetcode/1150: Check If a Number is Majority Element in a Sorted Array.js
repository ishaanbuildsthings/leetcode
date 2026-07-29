// https://leetcode.com/problems/check-if-a-number-is-majority-element-in-a-sorted-array/description/
// Difficulty: Easy
// tags: binary search

// Problem
/*
Simplified:
Input: nums = [2,4,5,5,5,5,5,6,6], target = 5
Output: true
Explanation: The value 5 appears 5 times and the length of the array is 9.
Thus, 5 is a majority element because 5 > 9/2 is true.

Input: nums = [10,100,101,101], target = 101
Output: false
Explanation: The value 101 appears 2 times and the length of the array is 4.
Thus, 101 is not a majority element because 2 > 4/2 is false.

Detailed:
Given an integer array nums sorted in non-decreasing order and an integer target, return true if target is a majority element, or false otherwise.

A majority element in an array nums is an element that appears more than nums.length / 2 times in the array.
*/

// Solution, O(log n) time and O(1) space.
/*
Do a binary search for the first occurrence of target. Using math, determine the last occurence of target that must be needed for it to be a majority.

We could also use a two pass solution that searches for the beginning and end, then determines if it is big enough.
*/

var isMajorityElement = function (nums, target) {
  let l = 0;
  let r = nums.length - 1;
  // binary search for the first instance of the target
  while (l < r) {
    const m = Math.floor((r + l) / 2);
    const num = nums[m];
    // if we found the number, or too big a number, we can/should look left, but include that number in case it is correct
    if (num >= target) {
      r = m;
    } else {
      l = m + 1;
    }
  }

  // verify we even found the number, can use l or r here
  if (nums[r] !== target) {
    return false;
  }

  const elementsNeededForMajority =
    nums.length % 2 === 0 ? nums.length / 2 + 1 : Math.ceil(nums.length / 2);

  const lastIndexThatShouldBeNumForMajority = r + elementsNeededForMajority - 1;

  if (nums[lastIndexThatShouldBeNumForMajority] === target) {
    return true;
  }

  return false;
};
