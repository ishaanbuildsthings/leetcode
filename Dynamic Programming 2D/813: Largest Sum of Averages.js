// https://leetcode.com/problems/largest-sum-of-averages/description/
// Difficulty: Medium
// Tags: Dynamic Programming 2d

// Problem
/*
You are given an integer array nums and an integer k. You can partition the array into at most k non-empty adjacent subarrays. The score of a partition is the sum of the averages of each subarray.

Note that the partition must use every integer in nums, and that the score is not necessarily an integer.

Return the maximum score you can achieve of all the possible partitions. Answers within 10-6 of the actual answer will be accepted.
*/

// Solution, O(n^2 * k) time, O(n*k) space
/*
For a given problem, we can make a split at some point, and the left region has no splits allowed, and the right region has splitsRemaining-1 splits allowed. This works since every region has a leftmost subregion with no more splits.
*/

ar largestSumOfAverages = function(nums, k) {
    // memo[l][splits left] tells us the answer to that subproblem
    const memo = new Array(nums.length).fill().map(() => new Array(k + 1).fill(-1));

    const prefixSums = [];
    let runningSum = 0;
    for (let i = 0; i < nums.length; i++) {
        runningSum += nums[i];
        prefixSums.push(runningSum);
    }
    prefixSums[-1] = 0;
    function rangeQueryAverage(l, r) {
        const rightPortion = prefixSums[r];
        const leftPortion = prefixSums[l - 1];
        return (rightPortion - leftPortion) / (r - l + 1);
    }

    function dp(l, splitsLeft) {
        // base case
        if (splitsLeft === 0) {
            return rangeQueryAverage(l, nums.length - 1);
        }

        // other base case
        if (l === nums.length - 1) {
            return nums[nums.length - 1];
        }

        if (memo[l][splitsLeft] !== -1) {
            return memo[l][splitsLeft];
        }

        let resultForThis = -Infinity;

        for (let splitPoint = l; splitPoint < nums.length - 1; splitPoint++) {
            const leftAverageIfSplitHere = rangeQueryAverage(l, splitPoint);
            const rightSubproblem = dp(splitPoint + 1, splitsLeft - 1);
            resultForThis = Math.max(resultForThis, leftAverageIfSplitHere + rightSubproblem);
        }

        memo[l][splitsLeft] = resultForThis;
        return resultForThis;
    }

    return dp(0, k - 1);
};