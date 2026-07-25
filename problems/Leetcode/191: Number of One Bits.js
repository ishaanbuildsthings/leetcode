// https://leetcode.com/problems/number-of-1-bits/description/
// Difficulty: Easy
// tags: Bit Manipulation

// Problem
/*
Example:

Input: n = 00000000000000000000000000001011
Output: 3
Explanation: The input binary string 00000000000000000000000000001011 has a total of three '1' bits.


Write a function that takes the binary representation of an unsigned integer and returns the number of '1' bits it has (also known as the Hamming weight).

Note:

Note that in some languages, such as Java, there is no unsigned integer type. In this case, the input will be given as a signed integer type. It should not affect your implementation, as the integer's internal binary representation is the same, whether it is signed or unsigned.
In Java, the compiler represents the signed integers using 2's complement notation. Therefore, in Example 3, the input represents the signed integer. -3.
*/

// Solution, O(1) time and O(1) space. Bit shift to the right using and operations to determine if the last bit is a 1.

var hammingWeight = function (n) {
  let result = 0;
  let current = n;

  while (current > 0) {
    if ((current & 1) === 1) {
      result++;
    }
    current = current >>> 1;
  }

  return result;
};
