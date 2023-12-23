// https://leetcode.com/problems/parallel-execution-of-promises-for-individual-results-retrieval/
// difficulty: medium

// Problem
// Given an array functions, return a promise promise. functions is an array of functions that return promises fnPromise. Each fnPromise can be resolved or rejected.

// If fnPromise is resolved:

//     obj = { status: "fulfilled", value: resolved value}

// If fnPromise is rejected:

//     obj = { status: "rejected", reason: reason of rejection (catched error message)}

// The promise should resolve with an array of these objects obj. Each obj in the array should correspond to the promises in the original array function, maintaining the same order.

// Try to implement it without using the built-in method Promise.allSettled().

// Solution, confusingly named question, it's just implementing Promise.allSettled. We can have each promise resolve to an object in the correct place, and we resolve the outer promise when all inner promises have resolved.

/**
 * @param {Array<Function>} functions
 * @return {Promise<Array>}
 */
var promiseAllSettled = function (functions) {
  return new Promise((res, rej) => {
    const result = [];
    let count = 0;
    functions.forEach((fn, i) => {
      const promise = fn();
      promise
        .then((val) => (result[i] = { status: "fulfilled", value: val }))
        .catch((e) => (result[i] = { status: "rejected", reason: e }))
        .finally(() => {
          count++;
          if (count === functions.length) {
            res(result);
          }
        });
    });
  });
};

/**
 * const functions = [
 *    () => new Promise(resolve => setTimeout(() => resolve(15), 100))
 * ]
 * const time = performance.now()
 *
 * const promise = promiseAllSettled(functions);
 *
 * promise.then(res => {
 *     const out = {t: Math.floor(performance.now() - time), values: res}
 *     console.log(out) // {"t":100,"values":[{"status":"fulfilled","value":15}]}
 * })
 */
