// https://leetcode.com/problems/missing-number/description/
// Difficulty: Easy
// tags: bit manipulation

// Problem
/*
Examples:

Input: nums = [3,0,1]
Output: 2
Explanation: n = 3 since there are 3 numbers, so all numbers are in the range [0,3]. 2 is the missing number in the range since it does not appear in nums.

Input: nums = [0,1]
Output: 2
Explanation: n = 2 since there are 2 numbers, so all numbers are in the range [0,2]. 2 is the missing number in the range since it does not appear in nums.

Detailed:
Given an array nums containing n distinct numbers in the range [0, n], return the only number in the range that is missing from the array.
*/

// Solution 1, O(n) time and O(1) space, one pass
// * Solution 2 is the original two pass solution I thought of
// * We can also do sum subtract to solve it
/*
Start with 0. XOR it with every number we are supposed to have, which we use the index for. Also XOR it with the number itself. This will reveal the missing number at the end.
*/
var missingNumber = function (nums) {
  let current = 0;
  for (let i = 0; i <= nums.length; i++) {
    current = current ^ i; // mod with the index
    current = current ^ nums[i]; // mod with the number itself
  }
  return current;
};

// Solution 2, O(n) time and O(1) space, two pass
/*
Start with 0, XOR it with every number we are supposed to have. Now XOR it with every number we actually do, revealing the missing number.
*/

var missingNumber = function (nums) {
  let current = 0;
  for (let i = 0; i <= nums.length; i++) {
    current = current ^ i;
  }

  for (const num of nums) {
    current = current ^ num;
  }

  return current;
};
