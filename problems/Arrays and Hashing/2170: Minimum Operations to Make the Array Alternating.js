// https://leetcode.com/problems/minimum-operations-to-make-the-array-alternating/description/
// difficulty: Medium

// Problem
/*
You are given a 0-indexed array nums consisting of n positive integers.

The array nums is called alternating if:

nums[i - 2] == nums[i], where 2 <= i <= n - 1.
nums[i - 1] != nums[i], where 1 <= i <= n - 1.
In one operation, you can choose an index i and change nums[i] into any positive integer.

Return the minimum number of operations required to make the array alternating.
*/

// Solution, O(n log n) time, O(n) space
/*
Since every other number (odd indexed and even indexed) must be the same, we can greedily set them to all be the most frequent number. But if the most frequent number is the same, we should make one of them into the second most frequent number. Basically just get the counts of otherthing, sort the frequencies, then greedily select.
*/

var minimumOperations = function (nums) {
  const countsFirst = {};
  const countsSecond = {};
  for (let i = 0; i < nums.length; i++) {
    const num = nums[i];
    if (i % 2 === 0) {
      if (!(num in countsFirst)) {
        countsFirst[num] = 1;
      } else {
        countsFirst[num]++;
      }
    }
    // if we have an odd idex, add to counts second
    else if (i % 2 === 1) {
      if (!(num in countsSecond)) {
        countsSecond[num] = 1;
      } else {
        countsSecond[num]++;
      }
    }
  }

  const countsFirstArr = []; // contains tuples of [num, freq]
  const countsSecondArr = [];

  for (const key in countsFirst) {
    const freq = countsFirst[key];
    countsFirstArr.push([key, freq]);
  }

  for (const key in countsSecond) {
    const freq = countsSecond[key];
    countsSecondArr.push([key, freq]);
  }

  const countsFirstArrSorted = [...countsFirstArr].sort((a, b) => b[1] - a[1]);
  const countsSecondArrSorted = [...countsSecondArr].sort(
    (a, b) => b[1] - a[1]
  );

  let totalNumsFirst;
  let totalNumsSecond;
  if (nums.length % 2 === 0) {
    totalNumsFirst = nums.length / 2;
    totalNumsSecond = nums.length / 2;
  } else {
    totalNumsFirst = Math.floor(nums.length / 2) + 1;
    totalNumsSecond = totalNumsFirst - 1;
  }

  countsFirstArrSorted.push([null, 0]);
  countsSecondArrSorted.push([null, 0]);

  if (countsFirstArrSorted[0][0] === countsSecondArrSorted[0][0]) {
    // if we let the first section use the most common number
    const option1 =
      totalNumsFirst -
      countsFirstArrSorted[0][1] +
      (totalNumsSecond - countsSecondArrSorted[1][1]);
    const option2 =
      totalNumsFirst -
      countsFirstArrSorted[1][1] +
      (totalNumsSecond - countsSecondArrSorted[0][1]);
    return Math.min(option1, option2);
  } else {
    const freq1 = countsFirstArrSorted[0][1];
    const freq2 = countsSecondArrSorted[0][1];
    return totalNumsFirst - freq1 + (totalNumsSecond - freq2);
  }
};
