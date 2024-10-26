// https://leetcode.com/problems/timeout-cancellation/description/
// difficulty: easy

// Problem
// Given a function fn, an array of arguments args, and a timeout t in milliseconds, return a cancel function cancelFn.

// After a delay of t, fn should be called with args passed as parameters unless cancelFn was invoked before the delay of t milliseconds elapses, specifically at cancelT ms. In that case, fn should never be called.

// Solution, O(1) time and space. We return a function that can cancel a closured value.

/**
 * @param {Function} fn
 * @param {Array} args
 * @param {number} t
 * @return {Function}
 */
var cancellable = function (fn, args, t) {
  let canceled = false;

  setTimeout(() => {
    if (canceled) return;
    fn(...args);
  }, t);

  const cancelFunction = () => {
    canceled = true;
  };
  return cancelFunction;
};
