// https://leetcode.com/problems/palindrome-number/description/
// Difficulty: Easy

// Problem
/*
Simplified: Determine whether an integer is a palindrome.
*/

// Take the input number and get the last digit, by modding 10. Multiply the number we are building by 10 to shift over all its values to the left, then add that last digit to a new number.
/*
243
243 % 10 = 3
new number *= 10, resulting in 0
add the 3
24 % 10 = 4
new number *= 10, resulting in 30
add the 4
...
*/

var isPalindrome = function (x) {
  const frozen = x;
  let secondNum = 0;
  while (x > 0) {
    const lastDigit = x % 10;
    secondNum *= 10;
    secondNum += lastDigit;
    x = Math.floor(x / 10);
  }
  return secondNum === frozen;
};
