// https://leetcode.com/problems/function-composition/description/
// Difficulty: Easy

// Problem
/*
Given an array of functions [f1, f2, f3, ..., fn], return a new function fn that is the function composition of the array of functions.

The function composition of [f(x), g(x), h(x)] is fn(x) = f(g(h(x))).

The function composition of an empty list of functions is the identity function f(x) = x.
*/

// Solution - read comments

var compose = function (functions) {
  // the reduction of functions takes in a callback, for any two functions acc and fn, we need a function which is acc(fn(x)), for instance f(x) and g(x), we need f(g(x)), then later that new function will be acc, and when we reach h(x), we will do acc(h(x)), which is f(g(h(x)))
  return functions.reduce(
    (acc, fn) =>
      function (x) {
        return acc(fn(x));
      },
    // default value in case the array is empty, return the identity function
    (x) => x
  );
};
