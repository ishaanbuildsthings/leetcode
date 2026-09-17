// https://leetcode.com/problems/minimum-moves-to-equal-array-elements-ii/description/
// difficulty: medium
// tags: prefix, binary search

// Problem
/*
Given an integer array nums of size n, return the minimum number of moves required to make all array elements equal.

In one move, you can increment or decrement an element of the array by 1.

Test cases are designed so that the answer will fit in a 32-bit integer.
*/

// Solution, O(n log n) time, O(n) space
/*
The minimum number of moves would always require setting all numbers to one of the numbers itself, not some number inbetween. This kind of needs a proof though. We can sort the array, then for each unique number, find the sum of the numbers on the left and the right and calculate the differences needed.
*/

var minMoves2 = function (nums) {
  nums.sort((a, b) => a - b);
  const sum = nums.reduce((acc, val) => acc + val, 0);

  const prefixSums = [];
  let runningSum = 0;
  for (let i = 0; i < nums.length; i++) {
    runningSum += nums[i];
    prefixSums.push(runningSum);
  }
  prefixSums[-1] = 0;

  function rangeQuery(l, r) {
    const rightPortion = prefixSums[r];
    const leftPortion = prefixSums[l - 1];
    return rightPortion - leftPortion;
  }

  let result = Infinity;

  for (let i = 0; i < nums.length; i++) {
    // find the leftmost occurence of that number
    let leftmostIndex;

    let l = 0;
    let r = nums.length - 1;
    while (l <= r) {
      const m = Math.floor((r + l) / 2); // m is the index of the number we look at
      if (nums[m] >= nums[i]) {
        r = m - 1;
      } else {
        l = m + 1;
      }
    }
    leftmostIndex = r + 1;

    // find the rightmost occurence of that number
    let rightmostIndex;
    l = 0;
    r = nums.length - 1;
    while (l <= r) {
      const m = Math.floor((r + l) / 2);
      if (nums[m] <= nums[i]) {
        l = m + 1;
      } else {
        r = m - 1;
      }
    }
    rightmostIndex = r;
    const leftPortionSum =
      leftmostIndex === 0 ? 0 : rangeQuery(0, leftmostIndex - 1);
    const rightPortionSum = rangeQuery(rightmostIndex + 1, nums.length - 1);
    const numsOnLeft = leftmostIndex;
    const numsOnRight = nums.length - rightmostIndex - 1;
    const leftChanges = numsOnLeft * nums[i] - leftPortionSum;
    const rightChanges = rightPortionSum - numsOnRight * nums[i];
    const totalChanges = leftChanges + rightChanges;
    result = Math.min(result, totalChanges);
  }

  return result;
};
