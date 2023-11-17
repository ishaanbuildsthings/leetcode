// https://leetcode.com/problems/promise-time-limit/
// Difficulty: medium

// Problem
// Given an asynchronous function fn and a time t in milliseconds, return a new time limited version of the input function. fn takes arguments provided to the time limited function.

// The time limited function should follow these rules:

// If the fn completes within the time limit of t milliseconds, the time limited function should resolve with the result.
// If the execution of the fn exceeds the time limit, the time limited function should reject with the string "Time Limit Exceeded".

// Solution
// We need to way to early reject if time runs out. We can just set a timeout to reject after that much time, but if the function itself finishes we take what that gives us.

var timeLimit = function (fn, t) {
  return function (...args) {
    return new Promise((res, rej) => {
      setTimeout(() => {
        rej("Time Limit Exceeded");
      }, t);
      fn(...args)
        .then((val) => res(val))
        .catch(rej); // see how it can be written both ways
    });
  };
};

// The issue with this is we have this enqueued set timeout which still runs later, though it doesn't change anything since a promise can only be resolved/rejected once. But we should still clear it from memory.

var timeLimit = function (fn, t) {
  return function (...args) {
    return new Promise((res, rej) => {
      const id = setTimeout(() => {
        rej("Time Limit Exceeded");
      }, t);
      fn(...args)
        .then((val) => res(val))
        .catch(rej) // see how it can be written both ways
        .finally(() => clearTimeout(id));
    });
  };
};

// We can also just race:
var timeLimit = function (fn, t) {
  return async function (...args) {
    const timeLimitPromise = new Promise((_, reject) => {
      setTimeout(() => reject("Time Limit Exceeded"), t);
    });
    const returnedPromise = fn(...args);
    return Promise.race([timeLimitPromise, returnedPromise]);
  };
};

// We can use async await for the fn, the idea is the setTimeout still is running and might trigger first, rejecting the promise
// I'm not sure what happens to the timeline that is awaiting the fn promise, I think it might still run but the result is ignored?
var timeLimit = function (fn, t) {
  return async function (...args) {
    return new Promise(async (resolve, reject) => {
      const timeout = setTimeout(() => {
        reject("Time Limit Exceeded");
      }, t);

      try {
        const result = await fn(...args);
        resolve(result);
      } catch (err) {
        reject(err);
      }
      clearTimeout(timeout);
    });
  };
};
