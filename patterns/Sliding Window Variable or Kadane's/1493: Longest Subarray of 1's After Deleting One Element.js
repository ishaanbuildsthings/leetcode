// https://leetcode.com/problems/longest-subarray-of-1s-after-deleting-one-element/description/
// Difficulty: medium
// tags: sliding window variable

// Problem
/*
Example:

Input: nums = [0,1,1,1,0,1,1,0,1]
Output: 5
Explanation: After deleting the number in position 4, [0,1,1,1,1,1,0,1] longest subarray with value of 1's is [1,1,1,1,1].

Detailed:
Given a binary array nums, you should delete one element from it.

Return the size of the longest non-empty subarray containing only 1's in the resulting array. Return 0 if there is no such subarray.
*/

// Solution, O(n) time and O(1) space, typical variable sliding window, iterate until we have two 0s, then decrement until we have one.
var longestSubarray = function (nums) {
  let result = 0;
  let l = 0;
  let r = 0;
  let seenZeroes = 0;
  while (r < nums.length) {
    if (nums[r] !== 0) {
      result = Math.max(result, r - l + 1 - seenZeroes);
    }
    // if we see a 0, we either just keep moving if its our first, or decrement from the left if needed
    else {
      // if we need to decrement from the left
      if (seenZeroes === 1) {
        // iterate until we reach a 0
        while (nums[l] !== 0) {
          l++;
        }
        // then clear the 0
        l++;
      } else if (seenZeroes === 0) {
        seenZeroes++;
      }
    }

    r++;
  }

  // since we have to delete one element
  if (seenZeroes === 0) {
    return result - 1;
  }

  return result;
};
