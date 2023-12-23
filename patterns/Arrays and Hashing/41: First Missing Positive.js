// https://leetcode.com/problems/first-missing-positive/description/
// Difficulty: Hard

// Problem
/*
Given an unsorted integer array nums, return the smallest missing positive integer.

You must implement an algorithm that runs in O(n) time and uses constant extra space.

Input: nums = [1,2,0]
Output: 3
Explanation: The numbers in the range [1,2] are all in the array.
*/

// Constraints
/*
Constraints:

1 <= nums.length <= 105
-231 <= nums[i] <= 231 - 1
*/

// Solution, O(n) time and O(1) space, does not preserve the input array
/*
To find the first missing positive, we can assign numbers in the array to be negative, based on their indices, to determine which numbers haven't been seen. For instance in the array [2,2,3], we see the number 2, and we can make the second number negative. Same thing with the 3, we can make the 3 itself negative because its at the third position. We have to use 1-indexing, because worst case all numbers are in the array, [1, 2, 3] and we should be able to mark them all negative, so we know 4 is missing. The problem is in this problem, negative numbers are allowed. This ruins our negative trick since we cannot tell if we marked a number negative due to its index, or that number was already negative. But since we don't care about negatives, we can iterate through and overwrite them with 1s. We cannot overwrite them with 0s, which would normally be great since then we could just ignore them, because if we try to make those 0s negative, we couldn't tell as -0 === 0. But if we use 1s, we cannot tell if a 1 is really in our array, so we have to check that first.
*/

var firstMissingPositive = function (nums) {
  let foundOne = false;
  for (let i = 0; i < nums.length; i++) {
    if (nums[i] === 1) {
      foundOne = true;
    }
    if (nums[i] <= 0) {
      nums[i] = 1;
    }
  }

  console.log(nums);

  if (!foundOne) {
    return 1;
  }

  for (let i = 0; i < nums.length; i++) {
    const number = Math.abs(nums[i]);
    // we can't assign a number out of bounds
    if (number > nums.length) {
      continue;
    }

    if (nums[number - 1] > 0) {
      nums[number - 1] *= -1;
    }
  }

  for (let i = 1; i < nums.length; i++) {
    if (nums[i] >= 0) {
      console.log(nums);
      return i + 1;
    }
  }

  return nums.length + 1;
};
