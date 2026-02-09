// https://leetcode.com/problems/contains-duplicate-ii/description/
// Difficulty: Easy
// tags: sliding window fixed

// Problem
/*
Simplfied: return true if there are two of the same numbers in any fixed sliding window, for all windows

Given an integer array nums and an integer k, return true if there are two distinct indices i and j in the array such that nums[i] == nums[j] and abs(i - j) <= k.
*/

// Solution
// O(n) time and O(k) space, as we at most track the number of elements in the window. Create a set that tracks if a number is currently in the fixed sliding window. We don't need to worry about quantity, since if we ever reach a duplicate, we can immediately return true. Iterate over the array with a fixed window and update the set.

var containsNearbyDuplicate = function (nums, k) {
  const windowWidth = k + 1; // fix weird indexing
  const windowWidthFinal = Math.min(windowWidth, nums.length); // reduce window if it is bigger than the array
  const elementsInWindow = new Set(); // tracks numbers currently in the window
  let l = 0;
  let r = windowWidthFinal - 1;

  for (let i = 0; i < windowWidthFinal; i++) {
    if (elementsInWindow.has(nums[i])) {
      return true;
    } else {
      elementsInWindow.add(nums[i]);
    }
  }

  while (r < nums.length - 1) {
    // we increment the left pointer, removing its value
    elementsInWindow.delete(nums[l]);
    l++;
    // we increment the right pointer, adding its value and seeing if it is in the window
    r++;
    if (elementsInWindow.has(nums[r])) {
      return true;
    } else {
      elementsInWindow.add(nums[r]);
    }
  }
  return false;
};
