// https://leetcode.com/problems/partial-function-with-placeholders/description/
// difficulty: easy

// Problem
// Given a function fn and an array args, return a function partialFn.

// Placeholders "_" in the args should be replaced with values from restArgs starting from index 0. Any remaining values in the restArgs should be added at the end of the args.

// partialFn should return a result of fn. fn should be called with the elements of the modified args passed as separate arguments.

// Solution
// I initially wrote it out verbosely, then condensed it to be functional.
// Note that ...restArgs CANNOT go in partial. The rest args are captured when you call that function. The whole point of this code is we execute partial to get another function we can use later and pass arbitrary args to it.

var partial = function (fn, args) {
  // the partial function we return
  return function (...restArgs) {
    let restArgsPointer = 0;
    const replacedArgs = args.map((arg) =>
      arg === "_" ? restArgs[restArgsPointer++] : arg
    );
    const finalArgs = [...replacedArgs, ...restArgs.slice(restArgsPointer)];
    return fn(...finalArgs);
  };
};
