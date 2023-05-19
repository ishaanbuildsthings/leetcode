// https://leetcode.com/problems/next-greater-element-ii/description/
// Difficulty: Medium

// Problem
/*
Simplified: Given an input array, find the next greatest element and construct the output. Put -1 if there is no next greatest. The array should be considered circularly.
Input: nums = [1,2,3,4,3]
Output: [2,3,4,-1,4]

Detailed:
Given a circular integer array nums (i.e., the next element of nums[nums.length - 1] is nums[0]), return the next greater number for every element in nums.

The next greater number of a number x is the first greater number to its traversing-order next in the array, which means you could search circularly to find its next greater number. If it doesn't exist, return -1 for this number.
*/

// Solution, O(n) time and O(n) space
// Solution walkthrough below the code. Short version is iterate through the array, maintaining a stack of elements and their indices. The stack is monotonically decreasing. When we find a bigger number, keep popping from the stack and updating a mapping. Then, iterate over it again. We don't need to worry about double-updating the indices in the mapping, since every time we store an index in the mapping we pop from the stack and cannot handle that index again.

var nextGreaterElements = function (nums) {
  const stack = []; // contains tuples
  const mapping = {}; // maps the index of a number to the next greater element, we have to use the index since there can be duplicates

  for (let i = 0; i < nums.length; i++) {
    // pop while our number is bigger
    while (stack.length > 0 && nums[i] > stack[stack.length - 1][0]) {
      const beatenTuple = stack[stack.length - 1];
      const index = beatenTuple[1];
      mapping[index] = nums[i];
      stack.pop();
    }
    // push the tuple
    stack.push([nums[i], i]);
  }

  for (let i = 0; i < nums.length; i++) {
    while (nums[i] > stack[stack.length - 1][0]) {
      const beatenTuple = stack[stack.length - 1];
      const index = beatenTuple[1];
      mapping[index] = nums[i];
      stack.pop();
    }
  }

  const result = new Array(nums.length).fill(-1);

  for (const key in mapping) {
    result[key] = mapping[key];
  }

  return result;
};

// 5 6 4

// we put a 5 and its index on the stack:
// [ [5,0]

// we put a 6 and its index, so we pop the 5, and update the mapping based on the index:
// [ [6,1]
// { 0:6 }, means number at position 0 has a next greater element of value 6

// we put a 4 and its index
// [ [6,1], [4,2]
// { 0:6 }

// we are at the end of the list, the elements not mapped are in the stack, so they dont have any bigger numbers to their right

// start iterating from the left again, up to and including the leftmost element of the stack, as that was the biggest element in the array

// we see a 5, its bigger than a 4, so pop the 4, and update the mapping
// [ [6,1]
// {0:6, 2:5}

// we see a 6, it's not bigger than the only element left in the stack (which happens to be the 6), so our loop completes, and every element in the array is assigned based on index

// anything still in the stack has a -1, which is the default value for our result
