// https://leetcode.com/problems/house-robber/description/
// Difficulty: Medium
// tags: dynamic programming 1d, bottom up recursion, top down recursion

// Problem
/*
Simplified:

Input: nums = [1,2,3,1]
Output: 4
Explanation: Rob house 1 (money = 1) and then rob house 3 (money = 3).
Total amount you can rob = 1 + 3 = 4.

Detailed:

You are a professional robber planning to rob houses along a street. Each house has a certain amount of money stashed, the only constraint stopping you from robbing each of them is that adjacent houses have security systems connected and it will automatically contact the police if two adjacent houses were broken into on the same night.

Given an integer array nums representing the amount of money of each house, return the maximum amount of money you can rob tonight without alerting the police.
*/

// Solution, O(n)  time and O(1) space, tabulation
/*
The rightmost and second to rightmost house are base cases. Seed those base cases. Then, iterate from the 3rd to last house. The amount we can get from this house is either the value at this house + the value of rob2 (two to the right). Or simply just the value we can get from the house to the right. Repeat this process, building up the tabulation.

We could also do this with recursion + memoization, but tabulation is more efficient on space, as we just maintain two pointers instead of a whole table.
*/

var rob = function (nums) {
  // edge case since we will start iterating from the 3rd to last element
  if (nums.length <= 2) {
    return Math.max(...nums);
  }

  // seed the initial tabulation values
  let rob2 = nums[nums.length - 1];
  let rob1 = Math.max(rob2, nums[nums.length - 2]);
  let currentRobbed = 0;

  // iterate from the 3rd to last element, to the beginning, going backwards
  for (let i = nums.length - 3; i >= 0; i--) {
    const option1 = nums[i] + rob2; // if we take the current house, we must skip the next
    const option2 = rob1; // if we don't take the current house, we can take the max from at the house on the right
    currentRobbed = Math.max(option1, option2);

    rob2 = rob1;
    rob1 = currentRobbed;
  }

  return currentRobbed;
};
