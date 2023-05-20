// https://leetcode.com/problems/remove-element/description/
// Difficulty: Easy

// Problem
/*
Simplified: Given an array of ints, and a value, remove all instances of that value in place. The order can be changed.
[0,1,2,2,3,0,4,2], val = 2
*/

// Solution
// O(n) time and O(1) space. Iterate over the array, if our number has the wrong value, swap it with the end, and pop the end, then check the swapped element again.

const removeElement = function (nums, val) {
  let l = 0;
  while (l < nums.length) {
    if (nums[l] === val) {
      nums[l] = nums[nums.length - 1];
      nums.pop();
    } else {
      l++;
    }
  }
};
