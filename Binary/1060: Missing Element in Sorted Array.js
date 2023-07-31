// https://leetcode.com/problems/missing-element-in-sorted-array/description/
// Difficulty: Medium
// Tags: binary search

// Problem
/*
Example:
Input: nums = [4,7,9,10], k = 3
Output: 8
Explanation: The missing numbers are [5,6,8,...], hence the third missing number is 8.

Detailed:
Given an integer array nums which is sorted in ascending order and all of its elements are unique and given also an integer k, return the kth missing number starting from the leftmost number of the array.
*/

// Solution, O(log n) time, O(log n) space for recursive callstack (could be O(1) space with iterative solution, recursive was just easier to reason about)
/*
Say we have some numbers:

4 7 9 10 20

and we want to find the fifth missing number

We can look at the left section [4, 7, 9], see that there should be 6 numbers here, but there are 3, meaning there are 3 missing numbers. Meaning we need to find the 2nd missing number in the right region. But actually we want the left region to be [4, 7, <one less than the number at m+1 index>] to make the ranges properly. If this doesn't make sense it's probably easier to reformalize exactly what our binary search is looking for (maybe first element with k missing elements to the left of it).
*/

var missingElement = function (nums, k) {
  // finds the kth missing number in [l:r]
  function recurse(l, r, kthMissing) {
    // base case
    if (l === r) {
      return nums[l] + kthMissing;
    }

    const m = Math.floor((r + l) / 2); // the index we look at

    const numbersShouldBeInLeft = nums[m + 1] - 1 - nums[l] + 1; // all numbers from [l, m] as well as all numbers up to, but not including the number to the right of the mth number
    const actualNumbersInLeft = m - l + 1;
    const missingNumbersInLeftRegion =
      numbersShouldBeInLeft - actualNumbersInLeft;

    if (missingNumbersInLeftRegion >= kthMissing) {
      return recurse(l, m, kthMissing);
    } else if (missingNumbersInLeftRegion < kthMissing) {
      const newMissing = kthMissing - missingNumbersInLeftRegion;
      return recurse(m + 1, r, newMissing);
    }
  }

  return recurse(0, nums.length - 1, k);
};

/*
4 7 9 10 20

5,6,8,11,12... (missing nums)
we are looking for 5th missing number


look at 9, we know there are 3 numbers from [4,9], out of 6 possible numbers, so 3 numbers are missing in this region, so we look strictly right


4 8 9 10 20
look at 9, there are 3 numbers from [4, 9] out of 6 that should be there, so the third missing number
*/
