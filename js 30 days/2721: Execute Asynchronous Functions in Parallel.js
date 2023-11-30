// https://leetcode.com/problems/execute-asynchronous-functions-in-parallel/
// difficulty: medium

// Problem
// Given an array of asynchronous functions functions, return a new promise promise. Each function in the array accepts no arguments and returns a promise. All the promises should be executed in parallel.

// promise resolves:

// When all the promises returned from functions were resolved successfully in parallel. The resolved value of promise should be an array of all the resolved values of promises in the same order as they were in the functions. The promise should resolve when all the asynchronous functions in the array have completed execution in parallel.
// promise rejects:

// When any of the promises returned from functions were rejected. promise should also reject with the reason of the first rejection.
// Please solve it without using the built-in Promise.all function.

// Solution
// Standard implementation, we just use a counter and resolve when each inner one does. Note that we can't do this code:
// return new Promise((res, rej) => {
//     const output = [];
//     let count = 0;
//     functions.forEach((fn, i) => {
//         fn().then((val) => {
//             output[i] = val;
//             if (++count === functions.length) {
//                 res(output);
//             }
//         }).catch((e) => rej(e))
//     });
// });
// because this is just putting the promises in the output, and promises don't transform, they pass their resolved values to .then, you also have a simple promise class implementation on notion which showcases this.

/**
 * @param {Array<Function>} functions
 * @return {Promise<any>}
 */
var promiseAll = function (functions) {
  return new Promise((res, rej) => {
    const output = [];
    let count = 0;
    functions.forEach((fn, i) => {
      fn()
        .then((val) => {
          output[i] = val;
          if (++count === functions.length) {
            res(output);
          }
        })
        .catch((e) => rej(e));
    });
  });
};

/**
 * const promise = promiseAll([() => new Promise(res => res(42))])
 * promise.then(console.log); // [42]
 */
