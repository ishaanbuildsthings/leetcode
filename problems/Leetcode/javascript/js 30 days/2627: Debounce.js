// https://leetcode.com/problems/debounce/description/
// Difficulty: Easy

// Problem
// Given a function fn and a time in milliseconds t, return a debounced version of that function.

// A debounced function is a function whose execution is delayed by t milliseconds and whose execution is cancelled if it is called again within that window of time. The debounced function should also receive the passed parameters.

// For example, let's say t = 50ms, and the function was called at 30ms, 60ms, and 100ms. The first 2 function calls would be cancelled, and the 3rd function call would be executed at 150ms. If instead t = 35ms, The 1st call would be cancelled, the 2nd would be executed at 95ms, and the 3rd would be executed at 135ms.

// Debounce Schematic

// The above diagram shows how debounce will transform events. Each rectangle represents 100ms and the debounce time is 400ms. Each color represents a different set of inputs.

// Please solve it without using lodash's _.debounce() function.

// Solution, trying to use the ms a function was executed with Date.now() is brittle (no guarantee of accuracy for when code runs, multiple things can be called in the same ms, etc etc). Instead, we use id and clearing.

/**
 * @param {Function} fn
 * @param {number} t milliseconds
 * @return {Function}
 */
var debounce = function (fn, t) {
  let priorId = null;
  return function (...args) {
    if (priorId) {
      clearTimeout(priorId);
    }
    priorId = setTimeout(() => {
      fn(...args);
    }, t);
  };
};

/**
 * const log = debounce(console.log, 100);
 * log('Hello'); // cancelled
 * log('Hello'); // cancelled
 * log('Hello'); // Logged at t=100ms
 */
