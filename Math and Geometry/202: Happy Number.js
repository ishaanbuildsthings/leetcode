// https://leetcode.com/problems/happy-number/description/
// Difficulty: Easy

// Problem
/*
Write an algorithm to determine if a number n is happy.

A happy number is a number defined by the following process:

Starting with any positive integer, replace the number by the sum of the squares of its digits.
Repeat the process until the number equals 1 (where it will stay), or it loops endlessly in a cycle which does not include 1.
Those numbers for which this process ends in 1 are happy.
Return true if n is a happy number, and false if not.
*/

// Solution
// Iterate forever, and break if we see a repeat number (implying a cycle, or we reach 1).

var isHappy = function (n) {
  const seenNumbers = new Set();
  seenNumbers.add(n); // not needed, makes it 1 tick faster

  while (true) {
    const numString = String(n);
    let sum = 0;
    for (const char of numString) {
      const number = Number(char);
      const squared = number * number;
      sum += squared;
    }

    // happy
    if (sum === 1) {
      return true;
    }
    // implies a loop
    if (seenNumbers.has(sum)) {
      return false;
    }

    seenNumbers.add(sum);

    n = sum;
  }
};
