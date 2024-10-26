// https://leetcode.com/problems/find-all-numbers-disappeared-in-an-array/description/
// Difficulty: Easy

// Problem
/*
Given an array nums of n integers where nums[i] is in the range [1, n], return an array of all the integers in the range [1, n] that do not appear in nums.
Input: nums = [4,3,2,7,8,2,3,1]
Output: [5,6]
*/

// Solution 1, O(n) time and space. Add all the numbers to a set, then iterate through the range [1, n] and add the numbers that aren't in the set to the result array.
// * Solution 2 is better

var findDisappearedNumbers = function (nums) {
  const set = new Set();
  for (let i = 0; i < nums.length; i++) {
    set.add(nums[i]);
  }

  const result = [];

  for (let i = 1; i <= nums.length; i++) {
    if (!set.has(i)) {
      result.push(i);
    }
  }

  return result;
};

// Solution 2, O(n) time and O(1) space
/*
Iterate over the array, every time we see a number, say 4, we mark the 4th number (index 3) as a negative. Since numbers in the range are always positive, we can use a negative to easily indicate that that number (by its index) has been seen. For example: [4, 3, 1, 2, 3], when we see the 4, we make the 2 a -2. Do this for all numbers. Now, we iterate over the array again, and any number that is still positive means there was no number that pointed to that, so we construct our result. We also turn the negatives back into positives as we iterate to fix the array.
*/
var findDisappearedNumbers = function (nums) {
  for (let i = 0; i < nums.length; i++) {
    const num = Math.abs(nums[i]);
    const index = num - 1;
    if (nums[index] > 0) {
      nums[index] *= -1;
    }
  }

  const result = [];

  for (let i = 0; i < nums.length; i++) {
    if (nums[i] > 0) {
      result.push(i + 1);
    } else if (nums[i] < 0) {
      nums[i] *= -1;
    }
  }

  return result;
};
