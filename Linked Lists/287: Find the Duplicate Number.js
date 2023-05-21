// https://leetcode.com/problems/find-the-duplicate-number/description/
// Difficulty: Medium

// Problem
/*
Simplfied: You have an array of length n, and the numbers range from 1 to n-1. For instance [3, 1, 2, 3], the highest a number could be is basically the last index. One of the numbers is repeated at least one time, there is only one repeated number. Find that number in constant space.

Given an array of integers nums containing n + 1 integers where each integer is in the range [1, n] inclusive.

There is only one repeated number in nums, return this repeated number.

You must solve the problem without modifying the array nums and uses only constant extra space.
*/

// Solution, O(n) time and O(1) space
/*
Think of this array: [1, 3, 4, 2, 2]
Use the indices to determine pointers, every number will point to one number based on index, and nothing points to the beginning number since numbers cannot be 0. This means we definitely have a linked list cycle as all numbers are in range so there is no way to escape the list. The 1 points to 3 (index 1), points to 2 (index 3), point to 4 (index 2), points to 2 (index 4), forming a cycle as 2 things point to do: 1->3->2->4->2-> the 4 again. Since two things point to 4, and 4 was at index 2, there are at multiple 2s. Use slow and fast pointers and find the head of the cycle then return that index.
*/

var findDuplicate = function (nums) {
  let slow = 0;
  let fast = 0;
  while (true) {
    slow = nums[slow];
    fast = nums[nums[fast]];
    if (slow === fast) {
      break;
    }
  }

  let start = 0;
  while (start !== slow) {
    start = nums[start];
    slow = nums[slow];
  }

  return start;
};
