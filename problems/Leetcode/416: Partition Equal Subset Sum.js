// https://leetcode.com/problems/partition-equal-subset-sum/description/
// Difficulty: Medium
// tags: dynamic programming 2d

// Problem
/*
Example:

Input: nums = [1,5,11,5]
Output: true
Explanation: The array can be partitioned as [1, 5, 5] and [11].

Given an integer array nums, return true if you can partition the array into two subsets such that the sum of the elements in both subsets is equal or false otherwise.
*/

// Solution O(n*k), n is the number of elements, and k is the number of unique sums <= sum(nums)/2
// * Solution 2 is what I initially wrote, but I used the difference between the two partitions instead
/*
To partition the array, we need to see if we can form one section with exactly half. For each element, we can either add it, or not, then check a dp if we can reach the remaining goal sum in the remaining subarray.
*/

var canPartition = function (nums) {
  const sum = nums.reduce((acc, val) => acc + val, 0);
  // can't partition an odd amount
  if (sum % 2 === 1) {
    return false;
  }

  // if we put this amount in one partition, we have balanced them
  const goalForOneHalf = sum / 2;

  // memo[l][sum] tells us, if given a certain sum, and [l:] elements to consider, we can reach exactly the goal for one half
  const memo = new Array(nums.length)
    .fill()
    .map(() => new Array(goalForOneHalf).fill(-1));

  function dp(l, currSum) {
    // base case, we have no elements left to consider. i prune cases where we exceed the sum so this is the actual base case
    if (l === nums.length) {
      return false;
    }
    if (currSum + nums[l] === goalForOneHalf) {
      return true;
    }

    if (memo[l][currSum] !== -1) {
      return memo[l][currSum];
    }

    // we can either skip this number, or take it
    let canPartition = false;

    canPartition = dp(l + 1, currSum); // if we skip it

    if (!canPartition && currSum + nums[l] < goalForOneHalf) {
      canPartition = dp(l + 1, currSum + nums[l]);
    }

    memo[l][currSum] = canPartition;
    return canPartition;
  }

  return dp(0, 0);
};

// Solution 2, very similar but I used the differences in the partitions instead, trying to make that 0. It's almost the exact same, instead of either adding a 3 or not (which gives sum of 3 or 0), I either gain 3 or lose 3, making a diff of +3 or -3. It might be less efficient from memoizing negative values though.

var canPartition = function (nums) {
  // memo[i][diff] represents if a solution to make two partitions equal, is doable, for the subproblem [i, nums.length - 1], and a surplus of the left subarray of `diff`
  const memo = new Array(nums.length).fill().map(() => ({}));

  function dp(i, diff) {
    if (i === nums.length && diff === 0) {
      return true;
    }

    if (i === nums.length && diff !== 0) {
      return false;
    }

    if (memo[i][diff] !== undefined) {
      return memo[i][diff];
    }

    let canPartition = false;
    // option1, if we add the leftmost element to the left partition
    const addToLeft = dp(i + 1, diff + nums[i]);

    // optimization, only check the right case if needed
    let addToRight = false;
    if (!addToLeft) {
      addToRight = dp(i + 1, diff - nums[i]);
    }

    canPartition = addToLeft || addToRight;

    memo[i][diff] = canPartition;
    return canPartition;
  }

  return dp(0, 0);
};
