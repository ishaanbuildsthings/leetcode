// https://leetcode.com/problems/subarray-sum-equals-k/description/
// Difficulty: Medium
// tags: prefix, lop off

// Problem
/*
Given an array of integers nums and an integer k, return the total number of continuous subarrays whose sum equals to k. The numbers can be negative.
*/

// Solution
// O(n) time and O(n) space
/*
Iterate over the array, computing a sum. That sum will be used to update our prefix mapping, which maps prefix sums to the number of times they have occured. Consider: [1, 2, 3, 4, 5]

When we are at 1, our only prefixSum is 0 (the empty prefix), which occurs once. It means we can take our current sum, 1, and chop off a sum of 0, in one way, to get a resulting sum. Now we calculate our sum, 1, and add it to the map. At number 2, we have two prefixes. Chopping off the empty prefix from the leftmost part, or chopping off the empty prefix + the 1. We continue to do this and update our result. This works because at any point of the array, the possible things we can chop off are tracked, for instance if we are at 4, we can chop off [0], [0,1], [0...2], [0...3], and all of those get computed as we go along.
*/

const subarraySum = function (nums, k) {
  const prefixMap = { 0: 1 }; // maps prefixes to the # of times they have occured
  let totalSubarrays = 0;
  let currentSum = 0;

  for (const num of nums) {
    currentSum += num;

    if (currentSum - k in prefixMap) {
      totalSubarrays += prefixMap[currentSum - k];
    }

    if (currentSum in prefixMap) {
      prefixMap[currentSum]++;
    } else {
      prefixMap[currentSum] = 1;
    }
  }
  return totalSubarrays;
};
