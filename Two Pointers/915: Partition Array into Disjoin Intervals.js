// https://leetcode.com/problems/partition-array-into-disjoint-intervals/description/
// difficulty: Medium
// tags: two pointers

// Problem
/*
Example:

Input: nums = [5,0,3,8,6]
Output: 3
Explanation: left = [5,0,3], right = [8,6]

Detailed:
Given an integer array nums, partition it into two (contiguous) subarrays left and right so that:

Every element in left is less than or equal to every element in right.
left and right are non-empty.
left has the smallest possible size.
Return the length of left after such a partitioning.

Test cases are generated such that partitioning exists.
*/

// Solution, O(n) time and O(n) space
// * An O(1) space solution exists. Essentially we iterate through, tracking two partitions, and repartition if needed.
/*
Preprocess the biggest numbers to the left (inclusive), the biggest to the right (exclusive), then iterate through and find the earliest valid partition. We could change this to a 2-pass solution by only preprocessing the right data, and using a variable to store the largest to the left.
*/

var partitionDisjoint = function (nums) {
  const biggestOnLeft = []; // tells the biggest in [:r] inclusive
  const smallestOnRight = []; // tells us the smallest number on the right (not inclusive), [l:]

  // calculate biggest on left
  let biggestLeft = 0;
  for (let i = 0; i < nums.length; i++) {
    biggestLeft = Math.max(biggestLeft, nums[i]);
    biggestOnLeft[i] = biggestLeft;
  }

  // calculate smallest on right
  let smallestRight = Infinity;
  for (let i = nums.length - 1; i >= 0; i--) {
    smallestOnRight[i] = smallestRight;
    smallestRight = Math.min(smallestRight, nums[i]);
  }

  // get the earliest partition, iterate from including the first element, to including n-1 elements
  for (let i = 0; i < nums.length - 1; i++) {
    const maxOnLeft = biggestOnLeft[i];
    const smallestToRight = smallestOnRight[i];
    if (maxOnLeft <= smallestToRight) {
      return i + 1; // we return length
    }
  }
};
