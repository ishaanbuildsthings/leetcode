// https://leetcode.com/problems/single-number/description/
// Difficulty: Easy
// tags: bit manipulation

// Problem
/*
Given a non-empty array of integers nums, every element appears twice except for one. Find that single one.

You must implement a solution with a linear runtime complexity and use only constant extra space.
*/

// Solution, O(n) time and O(1) space
/*
We XOR all the numbers in the array starting with 0, therefore being left with the remaining number. Since a ^ b ^ a = b, and a ^ a = 0, and a ^ 0 = a.
*/

var singleNumber = function (nums) {
  let result = 0;
  for (const num of nums) {
    result = result ^ num;
  }
  return result;
};
