// https://leetcode.com/problems/maximum-sum-with-exactly-k-elements/description/
// Difficulty: Easy

// Problem
/*
Simplfied: Take the max number and replace it with max+1, k times. Each time we replace the max, add it to our score. Return our max score.

Detailed:
You are given a 0-indexed integer array nums and an integer k. Your task is to perform the following operation exactly k times in order to maximize your score:

Select an element m from nums.
Remove the selected element m from the array.
Add a new element with a value of m + 1 to the array.
Increase your score by m.
Return the maximum score you can achieve after performing the operation exactly k times.
*/

// Solution
// O(n) time to locate the max, O(1) space
/*
Use math to compute the max return value. If we replace a value over and over, we can determine the sum to be a function of that initial value, the amount of times we replace it, and a triangle number formula */
var maximizeSum = function (nums, k) {
  const max = nums.reduce((acc, val) => Math.max(acc, val));
  const num1 = max * k;
  const triangle = (k * (k - 1)) / 2;
  return num1 + triangle;
};

// 0 + 1 + 2 + 3

// n(n - 1) / 2

// 1->0
// 2->1
// 3->3
// 4->6
