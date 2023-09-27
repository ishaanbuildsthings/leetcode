// https://leetcode.com/problems/array-reduce-transformation/
// Difficulty: Medium

// Problem
/*
Given an integer array nums, a reducer function fn, and an initial value init, return a reduced array.

A reduced array is created by applying the following operation: val = fn(init, nums[0]), val = fn(val, nums[1]), val = fn(val, nums[2]), ... until every element in the array has been processed. The final value of val is returned.

If the length of the array is 0, it should return init.

Please solve it without using the built-in Array.reduce method.
*/

// Solution, O(n) time and O(1) space
/**
 * @param {number[]} nums
 * @param {Function} fn
 * @param {number} init
 * @return {number}
 */
var reduce = function (nums, fn, init) {
  let current = init;
  for (const element of nums) {
    current = fn(current, element);
  }
  return current;
};
