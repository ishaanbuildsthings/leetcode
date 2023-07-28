// https://leetcode.com/problems/minimize-maximum-of-array/description/
// difficulty: Medium
// tags: binary search, prefix

// Problem
/*
You are given a 0-indexed array nums comprising of n non-negative integers.

In one operation, you must:

Choose an integer i such that 1 <= i < n and nums[i] > 0.
Decrease nums[i] by 1.
Increase nums[i - 1] by 1.
Return the minimum possible value of the maximum integer of nums after performing any number of operations.
*/

// Solution, O(n log n) time, O(1) space
/*
Essentially, we kind of push over numbers. So we can use binary search, and push over numbers starting from the right to see if we can use that as the maximum.
*/

var minimizeArrayValue = function (nums) {
  let l = 0;
  let r = nums.reduce((acc, val) => acc + val, 0); // worst case, the smallest maximum is the sum of all numbers

  while (l < r) {
    const m = Math.floor((r + l) / 2); // m is the smallest max we will try

    // greedily see if we can keep the numbers under m
    let carry = 0;
    for (let i = nums.length - 1; i >= 1; i--) {
      if (nums[i] + carry > m) {
        const surplus = nums[i] + carry - m;
        carry = surplus;
      } else {
        carry = 0;
      }
    }

    // if we couldn't fit it all, we need to try a bigger smallest max
    if (nums[0] + carry > m) {
      l = m + 1;
    } else {
      r = m;
    }
  }

  return r;
};
