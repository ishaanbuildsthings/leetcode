// https://leetcode.com/problems/keep-multiplying-found-values-by-two/description/
// Difficulty: Easy

// Problem
/*
You are given an array of integers nums. You are also given an integer original which is the first number that needs to be searched for in nums.

You then do the following steps:

If original is found in nums, multiply it by two (i.e., set original = 2 * original).
Otherwise, stop the process.
Repeat this process with the new number as long as you keep finding the number.
Return the final value of original.
*/

// Solution, O(n log n) time, O(sort) space
// * Can easily be O(n) time and O(n) space with a hashset, was just lazy to implement it
/*
Sort the numbers, then iterate through doubling original as it is found. Sorting makes it so we see the numbers in order. For instance if we have 4, 2, and original is 2, we would miss the 4.
*/

var findFinalValue = function (nums, original) {
  nums.sort((a, b) => a - b);
  let result = original;
  for (let i = 0; i < nums.length; i++) {
    if (nums[i] === result) {
      result *= 2;
    }
  }

  return result;
};
