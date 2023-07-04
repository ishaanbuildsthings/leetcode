// https://leetcode.com/problems/burst-balloons/description/
// Difficulty: Hard
// tags: dynamic programming 2d

// Problem
/*
You are given n balloons, indexed from 0 to n - 1. Each balloon is painted with a number on it represented by an array nums. You are asked to burst all the balloons.

If you burst the ith balloon, you will get nums[i - 1] * nums[i] * nums[i + 1] coins. If i - 1 or i + 1 goes out of bounds of the array, then treat it as if there is a balloon with a 1 painted on it.

Return the maximum coins you can collect by bursting the balloons wisely.
*/

// Solution, O(n^3) time and O(n^2) space
/*
This is a very difficult problem. Brute force would be try popping balloons in every order, which is n! states. We could memoize things, so if we have 1,2,3 as our balloons, popping 2 then 3 leads the same state as 3 then 2. Here, there are 2^n states, as we either have a balloon or we don't. This is still too many. We can try to reduce to n^2 subarray states and develop a recurrence relationship there.

Naively, if we try to pop some balloon, we are left with a subproblem on the left and right, but the issue is those subarrays are actually connected / contigent on each other. In 1,2,3, if we pop the 2, we are left with [1] and [3], but the 1 and 3 are adjacent so we cannot isolate them to true subproblems.

Instead, we can consider a balloon in the range to be the LAST balloon in that range to be popped. Say 2 is the last balloon in the range popped. We gain some score of 2 * what is on the left of the range * what is on the right of the range. And we are left with the subproblems of [1] and [3], and their adjacency to 2 is preserved due to their positions in the range.

Since there must be some balloon in a range to be the last one popped in that range, we can test all of them, taking n time per state, and find the best.
*/
var maxCoins = function (nums) {
  const newNums = [1, ...nums, 1];
  // memo[l][r] corresponds to the solution for the subarray [l, r], based off of the augmented form of numbers
  const memo = new Array(newNums.length)
    .fill()
    .map(() => new Array(newNums.length).fill(-1));

  // returns the max amount of points we can get from a given subarray, assuming the balloons on the left and right are popped after
  function dp(l, r) {
    // once we try to consider the left or right portion of a nonexistent array, the score from that is 0
    if (l > r) {
      return 0;
    }

    if (memo[l][r] !== -1) {
      return memo[l][r];
    }

    let maxPoints = 0;
    // for every balloon in range, we can consider it to be the last balloon popped, if that is the case, the score we get is the left subarray plus the right
    for (let i = l; i <= r; i++) {
      const leftPortion = dp(l, i - 1);
      const rightPortion = dp(i + 1, r);
      const scoreWhenLastBalloonInRangeIsPopped =
        newNums[i] * newNums[l - 1] * newNums[r + 1];
      const totalScore =
        leftPortion + rightPortion + scoreWhenLastBalloonInRangeIsPopped;
      maxPoints = Math.max(maxPoints, totalScore);
    }

    memo[l][r] = maxPoints;
    return maxPoints;
  }

  // solves the problem from the non-augmented array
  return dp(1, newNums.length - 2);
};
