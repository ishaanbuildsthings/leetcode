// https://leetcode.com/problems/return-length-of-arguments-passed/description/
// Difficulty: Easy

// Problem
/*
Write a function argumentsLength that returns the count of arguments passed to it.
*/

// Solution, O(1) time and O(1) space
/*
We use the rest operator so regardless of the number of arguments, our function can accept that many arguments. We then access the array produced by the operator.
*/

var argumentsLength = function (...args) {
  return args.length;
};
