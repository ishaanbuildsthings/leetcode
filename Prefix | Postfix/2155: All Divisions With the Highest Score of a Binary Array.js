// https://leetcode.com/problems/all-divisions-with-the-highest-score-of-a-binary-array/description/
// Difficulty: Medium
// Tags: Prefix | Postfix

// Problem
/*
You are given a 0-indexed binary array nums of length n. nums can be divided at index i (where 0 <= i <= n) into two arrays (possibly empty) numsleft and numsright:

numsleft has all the elements of nums between index 0 and i - 1 (inclusive), while numsright has all the elements of nums between index i and n - 1 (inclusive).
If i == 0, numsleft is empty, while numsright has all the elements of nums.
If i == n, numsleft has all the elements of nums, while numsright is empty.
The division score of an index i is the sum of the number of 0's in numsleft and the number of 1's in numsright.

Return all distinct indices that have the highest possible division score. You may return the answer in any order.
*/

// Solution, O(n) time, O(1) space, just iterate through and maintain a count

var maxScoreIndices = function (nums) {
  let result = [];
  let maxScore = 0;

  const totalOnes = nums.reduce((acc, val) => acc + val, 0);
  let onesInLeft = 0;

  for (let dividingPoint = 0; dividingPoint <= nums.length; dividingPoint++) {
    const numberOfElementsInLeft = dividingPoint;
    const zeroesInLeft = numberOfElementsInLeft - onesInLeft;
    const onesInRight = totalOnes - onesInLeft;
    const scoreAtThisSplit = zeroesInLeft + onesInRight;
    if (scoreAtThisSplit > maxScore) {
      maxScore = scoreAtThisSplit;
      result = [dividingPoint];
    } else if (scoreAtThisSplit === maxScore) {
      result.push(dividingPoint);
    }
    if (nums[dividingPoint] === 1) {
      onesInLeft++;
    }
  }

  return result;
};
