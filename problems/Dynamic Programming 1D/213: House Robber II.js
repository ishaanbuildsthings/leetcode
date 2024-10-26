// https://leetcode.com/problems/house-robber-ii/description/
// Difficulty: Medium
// tags: dynamic programming 1d, bottom up recursion, top down recursion

// Problem
/*
Simplified:
Same as House Robber I, but the houses are in a circle now.

Input: nums = [2,3,2]
Output: 3
Explanation: You cannot rob house 1 (money = 2) and then rob house 3 (money = 2), because they are adjacent houses.

Detailed:
You are a professional robber planning to rob houses along a street. Each house has a certain amount of money stashed. All houses at this place are arranged in a circle. That means the first house is the neighbor of the last one. Meanwhile, adjacent houses have a security system connected, and it will automatically contact the police if two adjacent houses were broken into on the same night.

Given an integer array nums representing the amount of money of each house, return the maximum amount of money you can rob tonight without alerting the police.
*/

// Solution, O(n) time and O(1) space.

/*
If we have houses [5, 10, 3, 1], it means we can either rob from [5, 10, 3] or [10, 3, 1]. We just solve both naive house robber problems and take the max. See 198: House Robber for details on the naive, but the idea is maintaining a tabulation (can be done with 2 pointers) starting from the rightmost house, and determining how much we can rob at each house.
*/

var rob = function (nums) {
  /*
    if our houses are 1, 2, 3, 4, 5

    if we ever rob from 1, we cannot rob from 5, and vice versa.

    so solve the problems for 1, 2, 3, 4, and 2, 3, 4, 5, and take the max
    */

  // edge cases, so we can start iterating from the 3rd to last element properly, or 4th to last for the second case
  if (nums.length <= 3) {
    return Math.max(...nums);
  }

  // solve the first case, where we skip the first house
  let rob2 = nums[nums.length - 1];
  let rob1 = Math.max(rob2, nums[nums.length - 2]);
  let currentRobbed = 0;
  for (let i = nums.length - 3; i >= 1; i--) {
    currentRobbed = Math.max(nums[i] + rob2, rob1);
    rob2 = rob1;
    rob1 = currentRobbed;
  }

  const result1 = currentRobbed;

  // solve the second case, where we skip the last house
  currentRobbed = 0;
  rob2 = nums[nums.length - 2];
  rob1 = Math.max(rob2, nums[nums.length - 3]);
  for (let i = nums.length - 4; i >= 0; i--) {
    currentRobbed = Math.max(nums[i] + rob2, rob1);
    rob2 = rob1;
    rob1 = currentRobbed;
  }

  const result2 = currentRobbed;

  return Math.max(result1, result2);
};
