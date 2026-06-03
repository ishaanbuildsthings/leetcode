// https://leetcode.com/problems/allow-one-function-call/description/
// Difficulty: Easy

// Problem
/*
Given a function fn, return a new function that is identical to the original function except that it ensures fn is called at most once.

The first time the returned function is called, it should return the same result as fn.
Every subsequent time it is called, it should return undefined.
*/

// Solution
// We need to return a function that calls our provided fn, but only once. It should call fn with the arguments we supply to the returned function, hence ...args.

var once = function (fn) {
  let count = 0;
  return function (...args) {
    if (count === 1) return undefined;
    count++;
    return fn(...args);
  };
};
