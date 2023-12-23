// https://leetcode.com/problems/find-all-duplicates-in-an-array/description/
// Difficulty: Medium

// Problem
/*
Given an integer array nums of length n where all the integers of nums are in the range [1, n] and each integer appears once or twice, return an array of all the integers that appears twice.

You must write an algorithm that runs in O(n) time and uses only constant extra space.
*/

// Solution, O(n) time and O(1) space.
/*
Each element appears once or twice, and refers to some 1-indexed index in the array. So iterate through, marking the number at that index as negative. If it were already negative, we add it to the result, since elements appear at most twice. If elements can appear arbitrary amounts of times, we need a way to distinguish between: seeing for the first time, seeing for the second time (add to result), and seeing for the third or later time (don't add to result). We could use something else out of scope of the numbers, for instance adding 0.5 or stringifying the number or whatever. At the end we can repair the array if we like.
*/
var findDuplicates = function (nums) {
  const result = [];

  // iterate through the array, treat the number as a 1-indexed index. negate the nunber at that index. If that number was already negative, we saw it 1 time before, so add it to the result
  for (let i = 0; i < nums.length; i++) {
    const numAsIndex = Math.abs(nums[i]) - 1; // have to do annoying shifting because the numbers in the array are 1-indexed
    if (nums[numAsIndex] < 0) {
      result.push(numAsIndex + 1);
    }
    nums[numAsIndex] *= -1;
  }

  return result;
};
