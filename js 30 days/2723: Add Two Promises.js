//https://leetcode.com/problems/add-two-promises/description/
// Difficulty: Easy

// Problem
/*
Given two promises promise1 and promise2, return a new promise. promise1 and promise2 will both resolve with a number. The returned promise should resolve with the sum of the two numbers.
*/

// Solution, O(max(promise1, promise2)) time, O(1) space. Just add the promises. Can use await, Promise.all, or .then.

var addTwoPromises = async function (promise1, promise2) {
  const val1 = await promise1;
  const val2 = await promise2;
  return val1 + val2;
};
