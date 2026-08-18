// https://leetcode.com/problems/minimum-deletions-to-make-array-divisible/description/
// Difficulty: Hard
// Tags: math

// Problem
/*
You are given two positive integer arrays nums and numsDivide. You can delete any number of elements from nums.

Return the minimum number of deletions such that the smallest element in nums divides all the elements of numsDivide. If this is not possible, return -1.

Note that an integer x divides y if y % x == 0.
*/

// Solution
// * Solution 2, any number that divides an array of numbers also divides their GCD. Find the GCD then find the first number to divide that GCD.
/*
First, I sorted all the numbers, which takes O(n) time and O(sort) space. Then, for each number, I get its factors in O(root num) time. I maintain a set of the shared factors. So whenever I get new factors for a number, I iterate over and only keep the shared ones. Then I find the smallest shared factor which takes O(shared factors log shared factors) time and O(sort shared factors) space. When we get to the first shared factor in nums (which we also preprocess with a hashmap) we know how many elements we need.
*/

/**
 * @param {number[]} nums
 * @param {number[]} numsDivide
 * @return {number}
 */
var minOperations = function (nums, numsDivide) {
  nums.sort((a, b) => a - b);

  const memo = {};
  function getFactors(num) {
    if (num in memo) return memo[num];
    const factors = new Set();
    for (let i = 1; i <= Math.floor(Math.sqrt(num)); i++) {
      if (num % i === 0) {
        factors.add(i);
        factors.add(num / i);
      }
    }
    factors.add(num);
    memo[num] = factors;
    return factors;
  }

  const allSharedFactors = new Set();
  const initialFactors = getFactors(numsDivide[0]);
  for (const factor of Array.from(initialFactors)) {
    allSharedFactors.add(factor);
  }

  for (let i = 1; i < numsDivide.length; i++) {
    const newFactors = getFactors(numsDivide[i]);
    for (const factor of Array.from(allSharedFactors)) {
      if (!newFactors.has(factor)) {
        allSharedFactors.delete(factor);
      }
    }
  }

  const numMapping = {}; // maps a number to the number of elements before it you need to process before reaching this number for this first time

  for (let i = 0; i < nums.length; i++) {
    if (!(nums[i] in numMapping)) {
      numMapping[nums[i]] = i;
    }
  }

  const sharedFactorsArr = Array.from(allSharedFactors).sort((a, b) => a - b);

  for (let i = 0; i < sharedFactorsArr.length; i++) {
    if (sharedFactorsArr[i] in numMapping) {
      return numMapping[sharedFactorsArr[i]];
    }
  }

  return -1;
};
