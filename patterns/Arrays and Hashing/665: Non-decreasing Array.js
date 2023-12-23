//https://leetcode.com/problems/non-decreasing-array/description/
// Difficulty: Medium

// Problem
/*
Simplfied: Can you make an array monotonically increasing with at most one element change?

Detailed:
Given an array nums with n integers, your task is to check if it could become non-decreasing by modifying at most one element.

We define an array is non-decreasing if nums[i] <= nums[i + 1] holds for every i (0-based) such that (0 <= i <= n - 2).
*/

// Solution, O(n) time and O(1) space
/*
Iterate over the elements, looking for a bad pair, which is when the first element is bigger than the second, like [1, 5, 4]. If we see a bad pair, note that, if we see a second, we can never make it monotonically increasing in one change, because two elements on the right are smaller than one element on the left. If we do see our first bad pair, we can either:
1 2 5 3 6, we are looking at the pair [5,3], we can change the 3 to be a 5 (or 6). Or, we can change the 5 to be a 2 (or 3), depending on whichever works.
*/

var checkPossibility = function (nums) {
  let badPairSeenAlready = false;
  for (let i = 0; i < nums.length - 1; i++) {
    if (nums[i] > nums[i + 1]) {
      // if this is our second decreasing pair it is impossible
      if (badPairSeenAlready) {
        return false;
      }
      // if our bad pair is the very last possible pair then we can make it monotonically increasing
      if (i === nums.length - 2) {
        return true;
      }
      // if it is our first pair, change the first element
      if (i === 0) {
        nums[i] = nums[i + 1];
      }
      // 3 4 2 6, x=4, since 6 is >= 4, we can change 2 to be 4
      if (nums[i] <= nums[i + 2]) {
        nums[i + 1] = nums[i];
      }
      // 1 4 2 3 x=4, since 2 >= 1, we can change x to be 2 (or 1)
      else if (nums[i + 1] >= nums[i - 1]) {
        nums[i] = nums[i + 1];
      } else {
        return false;
      }
      badPairSeenAlready = true;
    }
  }
  return true;
};
