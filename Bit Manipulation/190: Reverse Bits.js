// https://leetcode.com/problems/reverse-bits/description/
// Difficulty: easy
// Tags: Bit Manipulation

// Problem
/*
Simplified: We are given an unsigned 32 bit integer, reverse it.
*/

// Solution, O(1) time and O(1) space.

/*
Take the number we are given, and get the last bit. Shift our working result over to the left to make room, and add the bit. Repeat for every bit. Since in JS we are using a signed representation, we need to >>> 0 interpret is as an unsigned int.
*/
var reverseBits = function (n) {
  let reversed = 0;

  // get the last bit, then shift our working number to the left, and add our new bit
  for (let i = 1; i <= 32; i++) {
    const lastBit = n & 1;
    n = n >>> 1; // next time we need the new last bit of n

    // shift over our reversed number
    reversed = reversed << 1;
    // add a digit to the end of the reversed number
    reversed = reversed | lastBit;
  }

  return reversed >>> 0; // interpret the negative as a positive, since we want to reverse an unsigned int
};
