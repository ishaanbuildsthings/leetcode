// https://leetcode.com/problems/jump-game-ii/description/
// Difficulty: Medium
// Tags: Dynamic Programming 1d, greedy

// Problem
/*
Note: It is guaranteed you can reach the end.

You are given a 0-indexed array of integers nums of length n. You are initially positioned at nums[0].

Each element nums[i] represents the maximum length of a forward jump from index i. In other words, if you are at nums[i], you can jump to any nums[i + j] where:

0 <= j <= nums[i] and
i + j < n
Return the minimum number of jumps to reach nums[n - 1]. The test cases are generated such that you can reach nums[n - 1].
*/

// Solution, O(n*k) time O(n) space
/*
Typical dp, just test all jumps for a given index. There is an O(n) time and O(1) greedy solution though.
*/
var jump = function (nums) {
  // memo[i] stores the answer to the subproblem for [i:]
  const memo = new Array(nums.length).fill(-1);

  function dp(i) {
    if (i >= nums.length - 1) {
      return 0;
    }

    if (memo[i] !== -1) {
      return memo[i];
    }

    let resultForThis = Infinity;

    const jumps = nums[i];
    for (let j = 1; j <= jumps; j++) {
      const ifJumpHere = 1 + dp(i + j);
      resultForThis = Math.min(resultForThis, ifJumpHere);
    }

    memo[i] = resultForThis;
    return resultForThis;
  }

  return dp(0);
};
