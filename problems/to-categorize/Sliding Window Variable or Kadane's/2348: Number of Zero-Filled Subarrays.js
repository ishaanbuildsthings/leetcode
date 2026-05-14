// https://leetcode.com/problems/number-of-zero-filled-subarrays/description/
// Difficulty: Medium
// tags: sliding window variable, kadane's

// Problem
/*
Simplified:

Input: nums = [1,3,0,0,2,0,0,4]
Output: 6
Explanation:
There are 4 occurrences of [0] as a subarray.
There are 2 occurrences of [0,0] as a subarray.
There is no occurrence of a subarray with a size more than 2 filled with 0. Therefore, we return 6.

Detailed:
Given an integer array nums, return the number of subarrays filled with 0.

A subarray is a contiguous non-empty sequence of elements within an array.
*/

// Solution 1, kadane's, O(n) time and O(1) space
/*
Maintain a count of the current in a row 0s. Whenever we see another 0, increment that count, then increment the result by the current count. Since each consectuive 0 adds another layer in the triangle numbers.
*/

var zeroFilledSubarray = function (nums) {
  let result = 0;

  let currentZeroes = 0;

  for (const num of nums) {
    if (num === 0) {
      currentZeroes++;
      result += currentZeroes;
    } else {
      currentZeroes = 0;
    }
  }

  return result;
};

// Solution 2, sliding window variable, O(n) time and O(1) space
// Same thing, just using a sliding window variable

var zeroFilledSubarray = function (nums) {
  let result = 0;

  let l = 0;
  let r = 0;
  while (r < nums.length) {
    // if we see a non 0, reset the window and update result
    if (nums[r] !== 0) {
      const length = r - l; // length of the 0s we had
      const triangleNumber = (length * (length + 1)) / 2;
      result += triangleNumber;
      r = r + 1;
      l = r;
      continue;
    }
    /* here we saw a 0 */
    r++;
  }

  result += ((r - l) * (r - l + 1)) / 2; // add last triangle number if our array ends with only 0s

  return result;
};
