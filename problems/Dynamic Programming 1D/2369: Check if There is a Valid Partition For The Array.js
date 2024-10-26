// https://leetcode.com/problems/check-if-there-is-a-valid-partition-for-the-array/description/
// Difficulty: Medium
// Tags: Dynamic Programming 1d

// Problem
/*
You are given a 0-indexed integer array nums. You have to partition the array into one or more contiguous subarrays.

We call a partition of the array valid if each of the obtained subarrays satisfies one of the following conditions:

The subarray consists of exactly 2, equal elements. For example, the subarray [2,2] is good.
The subarray consists of exactly 3, equal elements. For example, the subarray [4,4,4] is good.
The subarray consists of exactly 3 consecutive increasing elements, that is, the difference between adjacent elements is 1. For example, the subarray [3,4,5] is good, but the subarray [1,3,5] is not.
Return true if the array has at least one valid partition. Otherwise, return false.
*/

// Solution, O(n) time and O(n) space
/*
To find a partition, we can either shed off the left 2 or 3 elements then get a remaining subproblem. Just standard dp.
*/

var validPartition = function (nums) {
  // memo[l] tells us if [l:] is valid
  const memo = new Array(nums.length).fill(-1);

  function dp(l) {
    // base cases
    if (l === nums.length) {
      return true;
    }

    if (memo[l] !== -1) {
      return memo[l];
    }

    let resultForThis = false;

    // first case, we split at 2
    if (nums[l] === nums[l + 1]) {
      const newResult = dp(l + 2);
      resultForThis = newResult;
    }

    // second case, we split at three
    if (nums[l] === nums[l + 1] && nums[l] === nums[l + 2]) {
      const newResult = dp(l + 3);
      resultForThis = resultForThis || newResult;
    }

    // third case, we split at three increasing
    if (nums[l] === nums[l + 1] - 1 && nums[l] === nums[l + 2] - 2) {
      const newResult = dp(l + 3);
      resultForThis = resultForThis || newResult;
    }

    memo[l] = resultForThis;
    return resultForThis;
  }

  return dp(0);
};
