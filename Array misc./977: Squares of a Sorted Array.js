// https://leetcode.com/problems/squares-of-a-sorted-array/description/
// Difficulty: Easy
// tags: two pointers

// Solution
// O(n) time and O(1) space. Use two pointers to iterate over the array from the left and right, and add the square of the larger of the two to the result array.

const sortedSquares = function (nums) {
  const output = new Array(nums.length);
  let count = 0; // represents count of numbers inserted into output, used to track where to do the next insertion
  let l = 0;
  let r = nums.length - 1;
  while (l <= r) {
    if (Math.abs(nums[l]) > Math.abs(nums[r])) {
      output[output.length - 1 - count] = nums[l] * nums[l];
      l++;
    } else {
      output[output.length - 1 - count] = nums[r] * nums[r];
      r--;
    }
    count++;
  }
  return output;
};
