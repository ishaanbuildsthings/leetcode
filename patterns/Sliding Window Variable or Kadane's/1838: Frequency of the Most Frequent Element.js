// https://leetcode.com/problems/frequency-of-the-most-frequent-element/description/
// Difficulty: Medium
// tags: sliding window variable

// Problem
/*
Simplfied: We can do k operations that transform a number into a number one higher. Find the maximum frequency of any number in the array after doing at most k operations.

Detailed:
The frequency of an element is the number of times it occurs in an array.

You are given an integer array nums and an integer k. In one operation, you can choose an index of nums and increment the element at that index by 1.

Return the maximum possible frequency of an element after performing at most k operations.
*/

// Solution
// O(n log n) time and O(1) space
/*
Sort the input array, get something like: [1, 3, 4, 8, 13], k=5

Initialize a two pointer variable sliding window. Check the current subarray sum, and how many changes we would need to make to make all elements equal the element on the rightmost portion. If we can make that many changes, update the max and increment the window to try for even more, if we cannot, decrement from the left until our window is valid again.

Since our subarrays are sorted, we don't need to worry about trying to get all the elements of [1, 3, 4] to reach 3, for example, we would have tried that before when 3 was the max. As long as we can keep setting elements, we should keep incrementing. Once we have gone over the limit, incrementing would never add to the max, since the elements only get bigger. So we should decrement the smallest, which will give us back the most extra changes to work with.
*/
var maxFrequency = function (nums, k) {
  nums.sort((a, b) => a - b);
  let l = 0;
  let r = 0;
  let currentSum = 0;
  let maxFrequencies = 0;

  while (r < nums.length) {
    currentSum += nums[r];
    let windowLength = r - l + 1;
    let totalForAllSame = nums[r] * windowLength;
    let numChangesNeeded = totalForAllSame - currentSum;
    // if we are allowed to make that many changes, update the max
    if (numChangesNeeded <= k) {
      maxFrequencies = Math.max(maxFrequencies, windowLength);
    } else {
      while (numChangesNeeded > k) {
        l++;
        currentSum -= nums[l - 1];
        windowLength--;
        totalForAllSame = nums[r] * windowLength;
        numChangesNeeded = totalForAllSame - currentSum;
      }
    }
    r++;
  }

  return maxFrequencies;
};

// 3 7 6 3 5 9 8 6 3 4 5 6 7 7 3

// k=4

// 1 4 8 13 3
// k=4

// 1 3 4 5 5 5 5
