// https://leetcode.com/problems/minimize-the-maximum-difference-of-pairs/description/
// Difficulty: Medium
// Tags: binary search

// Problem
/*
You are given a 0-indexed integer array nums and an integer p. Find p pairs of indices of nums such that the maximum difference amongst all the pairs is minimized. Also, ensure no index appears more than once amongst the p pairs.

Note that for a pair of elements at the index i and j, the difference of this pair is |nums[i] - nums[j]|, where |x| represents the absolute value of x.

Return the minimum maximum difference among all p pairs. We define the maximum of an empty set to be zero.
*/

// Solution, O(n log max difference) time, O(sort) space
/*
First, sort the numbers since we just care about pairs. Clearly, if we have some numbers a, b, c, d, we would never use the pair (a, b), since numbers cannot be reused, we should greedily select (a, b).

Do a binary search on the result and a greedy linear scan to see if that many pairs is doable.
*/

var minimizeMax = function (nums, p) {
  nums.sort((a, b) => a - b);
  const maxDifference = nums[nums.length - 1] - nums[0];

  let l = 0;
  let r = maxDifference;
  while (l <= r) {
    const m = Math.floor((r + l) / 2); // m is the max difference we allow, and we see if it is possible

    let pairsFound = 0;
    for (let i = 0; i < nums.length - 1; i++) {
      const difference = Math.abs(nums[i + 1] - nums[i]);
      if (difference <= m) {
        pairsFound++;
        i++; // we cannot use the adjacent element anymore
      }
    }

    // if we found enough pairs for this distance, we can try a smaller distance
    if (pairsFound >= p) {
      r = m - 1;
    } else {
      l = m + 1;
    }
  }

  return l;
};
