// https://leetcode.com/problems/interval-cancellation/description/
// difficulty: easy

// Problem
// Given a function fn, an array of arguments args, and an interval time t, return a cancel function cancelFn.

// The function fn should be called with args immediately and then called again every t milliseconds until cancelFn is called at cancelT ms.

// Solution, O(1) time and space. We start an interval which first runs after the delay time. We grab the ID from the interval then clear it when the cancel function is called.

/**
 * @param {Function} fn
 * @param {Array} args
 * @param {number} t
 * @return {Function}
 */
var cancellable = function (fn, args, t) {
  fn(...args); // setInterval does not run the function immediately

  const id = setInterval(() => {
    fn(...args);
  }, t);

  const cancelExec = () => {
    clearInterval(id);
  };

  return cancelExec;
};
