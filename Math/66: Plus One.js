// https://leetcode.com/problems/plus-one/description/
// Difficulty: Easy

// Problem
/*
You are given a large integer represented as an integer array digits, where each digits[i] is the ith digit of the integer. The digits are ordered from most significant to least significant in left-to-right order. The large integer does not contain any leading 0's.

Increment the large integer by one and return the resulting array of digits.

Simplified: Given an array of digits representing a number, add one to that number.
*/

// Solution
// Iterate over the array backwards, adding one. If we see a 9, continue adding one the the prior digit. If we don't see a 9, increment and break. Don't forget edge case where we need to add a new digit to the number, like 99->100.

var plusOne = function (digits) {
  for (let i = digits.length - 1; i >= 0; i--) {
    if (digits[i] === 9) {
      digits[i] = 0;
    } else {
      digits[i]++;
      break;
    }
  }

  // we need add a new digit
  if (digits[0] === 0) {
    digits = [1, ...digits];
  }
  return digits;
};
