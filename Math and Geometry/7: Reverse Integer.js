// https://leetcode.com/problems/reverse-integer/description/
// Difficulty: Medium
// tags: math

// Problem

/*
Given a signed 32-bit integer x, return x with its digits reversed. If reversing x causes the value to go outside the signed 32-bit integer range [-231, 231 - 1], then return 0.

Assume the environment does not allow you to store 64-bit integers (signed or unsigned).
*/

// Solution, O(1) time and O(1) space
/*
Get the last digit repeatedly by doing num % 10;

Shift our result to the left by doing reverse *= 10, then add the last digit.

But before we shift it, since we may overflow, check if our number is bigger than (2**31 - 1) / 10.

I didn't feel like handling JS weird negative mods, so I just used a boolean to return the negated version if needed.
*/

var reverse = function (x) {
  let num = x;
  let reverse = 0;

  let negative = false;
  if (num < 0) {
    num *= -1;
    negative = true;
  }
  while (num > 0) {
    const lastDigit = num % 10;

    // if when we multiply our reversed number by 10, to make room for the last digit, it would exceed the signed range, then we should just return 0
    if ((2 ** 31 - 1) / 10 < reverse) {
      return 0;
    }

    reverse *= 10;
    reverse += lastDigit;
    num = Math.floor(num / 10);
  }

  if (negative) {
    return (reverse *= -1);
  }

  return reverse;
};
