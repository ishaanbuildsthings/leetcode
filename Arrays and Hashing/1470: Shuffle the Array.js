// https://leetcode.com/problems/shuffle-the-array/description/
// Difficulty: Easy

// Problem
/*
Given the array nums consisting of 2n elements in the form [x1,x2,...,xn,y1,y2,...,yn].

Return the array in the form [x1,y1,x2,y2,...,xn,yn].
*/

// Solution, O(n) time and O(1) space
/*
Self explanatory. If we want to in place fill we can use bit manipulation and use the first bits to store one number and the end bits to store the end number, provided the max size of a number is small enough.
*/

var shuffle = function (nums, n) {
  const result = [];
  for (let i = 0; i < nums.length / 2; i++) {
    result.push(nums[i]);
    result.push(nums[i + nums.length / 2]);
  }
  return result;
};
