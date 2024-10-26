// https://leetcode.com/problems/add-digits/description/
// Difficulty: Easy

// Problem
/*
Given an integer num, repeatedly add all its digits until the result has only one digit, and return it.
*/

// Solution, O(1) time and space due to capped number length.
/*
Run a while loop, and keep replacing the digits.
*/

var addDigits = function (num) {
  let current = num;
  // if it's over 9, we need to add all the digits
  while (current > 9) {
    let digitSum = 0;
    // grab all the digits
    while (current !== 0) {
      const lastDigit = current % 10;
      digitSum += lastDigit;
      current = Math.floor(current / 10);
    }
    current = digitSum;
  }
  return current;
};
