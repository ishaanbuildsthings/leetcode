// https://leetcode.com/problems/n-th-tribonacci-number/description/?envType=study-plan-v2&envId=dynamic-programming
// Difficulty: easy
// Tags: dynamic programming 1d

// Problem
/*
The Tribonacci sequence Tn is defined as follows:

T0 = 0, T1 = 1, T2 = 1, and Tn+3 = Tn + Tn+1 + Tn+2 for n >= 0.

Given n, return the value of Tn.
*/

// Solution, O(n) time and O(1) space.
/*
DP with 3 cells. Easy tabulation.
*/
var tribonacci = function (n) {
  let first = 0;
  let second = 1;
  let third = 1;

  if (n === 0) {
    return first;
  } else if (n === 1) {
    return second;
  } else if (n === 2) {
    return third;
  }

  // starting at the fourth number, going up until n-1
  for (let i = 3; i <= n; i++) {
    const fourth = first + second + third;
    first = second;
    second = third;
    third = fourth;
  }

  return third;
};

// 0, 1, 1, 2, 4

// 0  1  2  3  4 (Tn)
