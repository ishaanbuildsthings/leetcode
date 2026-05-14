// https://leetcode.com/problems/search-in-rotated-sorted-array-ii/description/
// difficulty: medium
// tags: binary search

// Problem
/*
There is an integer array nums sorted in non-decreasing order (not necessarily with distinct values).

Before being passed to your function, nums is rotated at an unknown pivot index k (0 <= k < nums.length) such that the resulting array is [nums[k], nums[k+1], ..., nums[n-1], nums[0], nums[1], ..., nums[k-1]] (0-indexed). For example, [0,1,2,4,4,4,5,6,6,7] might be rotated at pivot index 5 and become [4,5,6,6,7,0,1,2,4,4].

Given the array nums after the rotation and an integer target, return true if target is in nums, or false if it is not in nums.

You must decrease the overall operation steps as much as possible.
*/

// Solution, O(n) time worst case, O(1) space
/*
Similar to the normal rotated sorted array problem. The crux is to figure out which portion we are in and move accordingly based on the number we see relative to the target. Lots of if/else branches. Worst case is linear since sometimes we cannot deduce enough information.
*/

var search = function (nums, target) {
  let l = 0;
  let r = nums.length - 1;
  while (l < r) {
    const m = Math.floor((r + l) / 2); // m is the index of the number we analyze

    const num = nums[m];

    if (num === target) {
      return true;
    }

    // if the number is bigger than the leftmost, we are in the left portion of the array
    if (num > nums[0]) {
      // if the target is bigger than the rightmost number, the target exists in the left portion
      if (target > nums[nums.length - 1]) {
        // if our number is bigger than the target, we therefore look left to decrement
        if (num > target) {
          r = m;
        } else if (num < target) {
          l = m + 1;
        }
      }
      // if the target is smaller or equal to the rightmost number, the target resides in the right portion (or an edge case, where there is no right portion), since we are in the left portion, we look right
      else if (target <= nums[nums.length - 1]) {
        // edge case, we only have a left portion
        if (target >= nums[0]) {
          if (target > num) {
            l = m + 1;
          } else {
            r = m;
          }
        } else {
          l = m + 1;
        }
      }
    }

    // if the number is smaller than the leftmost, we are in the right portion of the array
    else if (num < nums[0]) {
      // if the target is bigger than the rightmost number, the target resides in the left portion, since the target is in the left and we are in the right, we look left
      if (target > nums[nums.length - 1]) {
        r = m;
      }
      // if the target is within the rightmost number, it exists in the right portion
      else if (target <= nums[nums.length - 1]) {
        // if the target is bigger than our number, we look right
        if (target > num) {
          l = m + 1;
        } else {
          r = m;
        }
      }
    }

    // if the numbers are equal, we are either in the right portion of the array and the entire right portion + nums[0] are all the same number, or we are in the left portion and the entire right portion + part of the left portion is the same number
    else if (num === nums[0]) {
      for (let i = l; i <= r; i++) {
        if (nums[i] === target) return true;
      }
      return false;
    }
  }

  return nums[l] === target;
};
