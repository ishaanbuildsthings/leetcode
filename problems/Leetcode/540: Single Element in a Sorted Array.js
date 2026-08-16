// https://leetcode.com/problems/single-element-in-a-sorted-array/description/
// Difficulty: Medium
// tags: binary search

// Problem
/*
Simplified:
Input: nums = [1,1,2,3,3,4,4,8,8]
Output: 2

Detailed:
You are given a sorted array consisting of only integers where every element appears exactly twice, except for one element which appears exactly once.

Return the single element that appears only once.

Your solution must run in O(log n) time and O(1) space.
*/

// Solution, O(log n) time and O(1) space
/*
We know each element occurs twice, except one. We can check if the element we are looking at in binary search occurs on the right, or on the left, and then determine the number of elements in the left search range or in the right search range. Whichever is odd is where we look. The way I implemented it checks how many pairs exist to know which way to look, which is a bit more cumbersome.
*/

var singleNonDuplicate = function (nums) {
  let l = 0;
  let r = nums.length - 1;
  let m = Math.floor((r + l) / 2);
  while (l < r) {
    m = Math.floor((r + l) / 2);
    // if we have an even number of pairs
    if (((r - l) / 2) % 2 === 0) {
      // right is same
      if (nums[m] === nums[m + 1]) {
        l = m + 2;
      }
      // left is same
      else if (nums[m] === nums[m - 1]) {
        r = m - 2;
      }
      // unique
      else {
        return nums[m];
      }
    } else {
      // right is same
      if (nums[m] === nums[m + 1]) {
        r = m - 1;
      }
      // left is same
      else if (nums[m] === nums[m - 1]) {
        l = m + 1;
      }
      // unique
      else {
        return nums[m];
      }
    }
  }

  return nums[l];
};
/*
1, 2, 2
   ^
   right is same, look left

1, 1, 2
   ^
   left is same, look right


   1, 2, 2, 3, 3
         ^
         left is same, look left
*/
