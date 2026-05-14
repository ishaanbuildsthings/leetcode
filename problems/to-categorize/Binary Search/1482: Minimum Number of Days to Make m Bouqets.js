// https://leetcode.com/problems/minimum-number-of-days-to-make-m-bouquets/description/
// difficulty: Medium
// tags: Binary Search

// Problem
/*
You are given an integer array bloomDay, an integer m and an integer k.

You want to make m bouquets. To make a bouquet, you need to use k adjacent flowers from the garden.

The garden consists of n flowers, the ith flower will bloom in the bloomDay[i] and then can be used in exactly one bouquet.

Return the minimum number of days you need to wait to be able to make m bouquets from the garden. If it is impossible to make m bouquets return -1.
*/

// Solution, O(n log n) time, O(1) space
/*
Do a binary search. Try a number of days, and with that days, greedily collect bouqets, see if we get enough.
*/

var minDays = function (bloomDay, m, k) {
  // handles edge case, even if we wait the max days it might not work, makes the binary search a bit easier
  if (bloomDay.length < m * k) {
    return -1;
  }

  let l = 0;
  let r = Math.max(...bloomDay); // worst case we have to wait the max number of days
  while (l < r) {
    const mid = Math.floor((r + l) / 2); // m is the number of days we try

    // sliding window
    let totalBoquets = 0;
    let currentStreak = 0;
    for (let i = 0; i < bloomDay.length; i++) {
      // if we can take a flower, increase our streak
      if (bloomDay[i] <= mid) {
        currentStreak++;
      }
      // if we cannot take the flower, reset the streak
      else {
        currentStreak = 0;
      }

      // if our streak is the number of flowers we need for a boquet, make one
      if (currentStreak === k) {
        currentStreak = 0;
        totalBoquets++;
      }
    }

    // if we don't have enough boquets, we need to try wait more days
    if (totalBoquets < m) {
      l = mid + 1;
    } else {
      r = mid;
    }
  }

  return r;
};
