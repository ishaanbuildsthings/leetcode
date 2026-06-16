// https://leetcode.com/problems/removing-minimum-and-maximum-from-array/description/
// Difficulty: Medium

// Problem
/*
You are given a 0-indexed array of distinct integers nums.

There is an element in nums that has the lowest value and an element that has the highest value. We call them the minimum and maximum respectively. Your goal is to remove both these elements from the array.

A deletion is defined as either removing an element from the front of the array or removing an element from the back of the array.

Return the minimum number of deletions it would take to remove both the minimum and maximum element from the array.
*/

// Solution, O(n) time, O(1) space
/*
Just try deleting from the left only, from the right only, and from both ends
*/

var minimumDeletions = function (nums) {
  let smallest = Infinity;
  let smallestIndex;
  let largest = -Infinity;
  let largestIndex;
  for (let i = 0; i < nums.length; i++) {
    if (nums[i] > largest) {
      largest = nums[i];
      largestIndex = i;
    }
    if (nums[i] < smallest) {
      smallest = nums[i];
      smallestIndex = i;
    }
  }

  let result = Infinity;

  // delete from the left only
  result = Math.max(smallestIndex, largestIndex) + 1;

  // delete from right only
  const deletionsFromRight =
    nums.length - Math.min(smallestIndex, largestIndex);
  result = Math.min(result, deletionsFromRight);

  console.log(result);

  // delete from left and right
  const leftDeletions = Math.min(smallestIndex, largestIndex) + 1;
  const rightDeletions = nums.length - Math.max(smallestIndex, largestIndex);
  result = Math.min(result, leftDeletions + rightDeletions);

  return result;
};
