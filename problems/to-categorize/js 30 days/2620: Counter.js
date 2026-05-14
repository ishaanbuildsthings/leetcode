// https://leetcode.com/problems/counter/description/
// Difficulty: Easy

// Problem
/*
Given an integer n, return a counter function. This counter function initially returns n and then returns 1 more than the previous value every subsequent time it is called (n, n + 1, n + 2, etc).
*/

// Solution
// It's just using a closure. Could also return n++ but it's less clear.

var createCounter = function (n) {
  let count = n - 1;
  return function () {
    count++;
    return count;
  };
};
