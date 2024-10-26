// https://leetcode.com/problems/sum-of-two-integers/description/
// Difficulty: Medium
// tags: Bit Manipulation

// Problem
// Given two integers a and b, return the sum of the two integers without using the operators + and -.

// Solution 1, O(1) time and O(1) space, XOR and carry sum, iterative
// * Many other solutions, see below
/*
If we want to sum two numbers, we can add their XORs, which gives us the sum without carrys. To get the carrys, we do (a & b) << 1, since the carries get shifted over.

We add two numbers by taking their XOR, and adding it to the carry. But if that causes another carry, we need to keep repeating it.
*/

var getSum = function (a, b) {
  let sum = a;
  let carry = b;
  while (carry !== 0) {
    const newSumWithoutCarry = sum ^ carry;
    const newCarry = (sum & carry) << 1;
    sum = newSumWithoutCarry;
    carry = newCarry;
  }
  return sum;
};

// * Can be simplified a bit:

var getSum = function (a, b) {
  let sum = a;
  let carry = b;
  while (carry !== 0) {
    const newCarry = (sum & carry) << 1;
    sum = sum ^ carry;
    carry = newCarry;
  }
  return sum;
};

// Recursive version:

var getSum = function (a, b) {
  let sumWithoutCarry = a ^ b;
  let carrySum = (a & b) << 1;

  if (!carrySum) return sumWithoutCarry;
  else return getSum(sumWithoutCarry, carrySum);
};

// Solution 2, my jank version which I first did. Add the last bits, and track a carry. Shift the bits to the left. Then reverse the whole thing at the end.

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

  return reversed;
};

var getSum = function (a, b) {
  let result = 0;
  let carry = false; // if we actively have to carry a bit
  // iterate through all bits
  for (let i = 1; i <= 32; i++) {
    const lastbitA = a & 1;
    const lastbitB = b & 1;

    // make room to add the new bit
    result = result << 1;

    // if we have one 1, one 0
    if (lastbitA !== lastbitB) {
      if (!carry) {
        result = result | 1;
      }
      // if we do have a carry, we would just set a 0 and then carry again, so nothing changes
      else {
      }
    }

    // if we have two 0s
    else if (!lastbitA && !lastbitB) {
      // if we have a carry, add a 1, otherwise we do nothing
      if (carry) {
        result = result | 1;
        carry = false;
      }
    }

    // if we have two 1s
    else {
      if (!carry) {
        carry = true;
      } else {
        result = result | 1;
      }
    }

    a = a >>> 1;
    b = b >>> 1;
  }

  return reverseBits(result);
};
