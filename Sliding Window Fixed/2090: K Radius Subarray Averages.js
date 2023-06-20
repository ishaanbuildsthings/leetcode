// https://leetcode.com/problems/k-radius-subarray-averages/description/
// Difficulty: Medium
// tags: sliding window fixed

// Problem
/*
Simpliied:
k=3
[7, 4, 3, 9, 1, 8, 5, 2, 6]
          ^
[    sum these     ]

Detailed:
You are given a 0-indexed array nums of n integers, and an integer k.

The k-radius average for a subarray of nums centered at some index i with the radius k is the average of all elements in nums between the indices i - k and i + k (inclusive). If there are less than k elements before or after the index i, then the k-radius average is -1.

Build and return an array avgs of length n where avgs[i] is the k-radius average for the subarray centered at index i.

The average of x elements is the sum of the x elements divided by x, using integer division. The integer division truncates toward zero, which means losing its fractional part.

For example, the average of four elements 2, 3, 1, and 5 is (2 + 3 + 1 + 5) / 4 = 11 / 4 = 2.75, which truncates to 2.
*/

var getAverages = function (nums, k) {
  // if k is so big that the entire array should be filled with -1, do so. helps because then our for loop that adds the first 2k elements won't cause problems
  if (k * 2 > nums.length) {
    return nums.map((_) => -1);
  }

  let runningSum = 0;
  for (let i = 0; i <= k * 2; i++) {
    runningSum += nums[i];
  }

  const result = new Array(nums.length).fill(-1); // we will fill all values with -1 and overwrite the ones that we can change

  let writePointer = k; // start at the first non -1 value
  const endingPoint = nums.length - k - 1;

  while (writePointer <= endingPoint) {
    const average = Math.floor(runningSum / (2 * k + 1));
    result[writePointer] = average;
    writePointer++;
    runningSum -= nums[writePointer - k - 1]; // lose the left number when we slide over
    runningSum += nums[writePointer + k]; // gain the right number when we slide, gets NaN on the last iteration but doesn't matter
  }

  return result;
};
