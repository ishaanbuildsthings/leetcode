// https://leetcode.com/problems/delay-the-resolution-of-each-promise/description/
// Difficulty: Easy

// Problem
// Given an array functions and a number ms, return a new array of functions.

// functions is an array of functions that return promises.
// ms represents the delay duration in milliseconds. It determines the amount of time to wait before resolving each promise in the new array.
// Each function in the new array should return a promise that resolves after a delay of ms milliseconds, preserving the order of the original functions array. The delayAll function should ensure that each promise from functions is executed with a delay, forming the new array of functions returning delayed promises.

// Solution
// Kind of a confusingly worded question. Basically I map each function to a new function that returns a promise. The promise runs a set timeout which after the delay runs the initial function and resolves or rejects the promise.

/**
 * @param {Array<Function>} functions
 * @param {number} ms
 * @return {Array<Function>}
 */
var delayAll = function (functions, ms) {
  return functions.map((fn) => {
    return () => {
      return new Promise((res, rej) => {
        setTimeout(() => {
          fn().then(res).catch(rej);
        }, ms);
      });
    };
  });
};
