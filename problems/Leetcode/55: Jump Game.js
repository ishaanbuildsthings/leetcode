// https://leetcode.com/problems/jump-game/description/
// Difficulty: Medium
// tags: bottom up recursion

// Problem
/*
Simplified:
Input: nums = [3,2,1,0,4]
Output: false
Explanation: You will always arrive at index 3 no matter what. Its maximum jump length is 0, which makes it impossible to reach the last index.

Detailed:
You are given an integer array nums. You are initially positioned at the array's first index, and each element in the array represents your maximum jump length at that position.

Return true if you can reach the last index, or false otherwise.
*/

// Solution, O(n) time and O(1) space.

/*
Start from the right, seeing the furthest left index that can reach the end. Iterate backwards, checking if we can reach that index, and if so, updating it. At the end, check if the first index can reach it.

This is better than recursion + memoization, since we might have an arbitrary amount of jumps. Even if we cache results we would do at most n lookups (if our jumping distance were exactly enough to almost reach the end, essentially upper bounded by n). This would make n^2 time. Still better than brute force, which is exponential.
*/

var canJump = function (nums) {
  let leftMostIndexThatCanReachEnd = nums.length - 1; // initially, to definitely reach the end, we would need to be able to go straight to the end

  // i represents the index we are at. we work backwards to see if we can reach the end.
  for (let i = nums.length - 2; i >= 0; i--) {
    const jumpDistance = nums[i];
    const furthestRightIndexWeCanReach = i + jumpDistance;
    if (furthestRightIndexWeCanReach >= leftMostIndexThatCanReachEnd) {
      leftMostIndexThatCanReachEnd = i;
    }
  }

  if (leftMostIndexThatCanReachEnd === 0) {
    return true;
  }

  return false;
};
