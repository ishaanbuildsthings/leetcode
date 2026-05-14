//https://leetcode.com/problems/continuous-subarray-sum/description/
// Difficulty: Medium

// Problem
/*
Simplfied: We have an array of positive integers. We need to see if there is a subarray that is good, which means the sum of that subarray is divisible by some number, k. The subarray must also be at least 2 in length. [0, 0] is considered good as well.

Detailed:
Given an integer array nums and an integer k, return true if nums has a good subarray or false otherwise.

A good subarray is a subarray where:

its length is at least two, and
the sum of the elements of the subarray is a multiple of k.
Note that:

A subarray is a contiguous part of the array.
An integer x is a multiple of k if there exists an integer n such that x = n * k. 0 is always a multiple of k.
*/

// Solution
// O(n) time and O(n) space
/*
Iterate over the array, maintaing a sum. We also will check the current remainder at any point, and add it to a map, which maps remainders to the first time they have occured. If we see a remainder twice, we know we could make a perfect divisible subarray. Consider: [4, 6] with k=6
At 4, our map becomes { 4 : 0 }
At 6, our remainder is still 4. This means our current sum is too big by 4. But we had another prefix subarray from the left that was too big by 4, so if we removed that, we could have a perfectly divisible subarray (though in this case, it's not long enough as per the indices)
*/

var checkSubarraySum = function (nums, k) {
  const modMap = {}; // contains numbers for the mod prefixes, mapped to the first index they occurred
  // for instance: [23, 2, 4], k=6
  /*
   at 23, our mod is 23%6=5, so we add { 5 : 0 }
   at 2, our sum is 25, and our mod is therefore 1, add { 1 : 1 }
   at 29, our mod is 5, that is in the dictionary and has index 0, which is at least 2 away
   */

  let currentSum = 0;
  for (let i = 0; i < nums.length; i++) {
    const num = nums[i];

    currentSum += num;
    const currentMod = currentSum % k;

    // if we have seen this mod before at least 2 spaces ago
    if (currentMod in modMap && i - modMap[currentMod] >= 2) {
      return true;
    }
    // if we haven't seen it at all, add it to the map
    else if (!(currentMod in modMap)) {
      modMap[currentMod] = i;
    }
    // if our current sum is perfect and we are at least at the second element
    if (currentSum % k === 0 && i >= 1) return true;
  }
  return false;
};
