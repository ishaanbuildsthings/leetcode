// https://leetcode.com/problems/concatenation-of-array/description/
// Difficulty: Easy

// Solution O(n) time and O(1) space

// make one pass over the array

const getConcatenation = function (nums) {
  const result = new Array(nums.length * 2);
  for (let i = 0; i < nums.length; i++) {
    result[i] = nums[i];
    result[i + nums.length] = nums[i];
  }
  return result;
};
