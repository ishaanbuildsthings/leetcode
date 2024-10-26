// https://leetcode.com/problems/repeat-string/description/
// difficulty: easy

// Problem
// Write code that enhances all strings such that you can call the string.replicate(x) method on any string and it will return repeated string x times.

// Try to implement it without using the built-in method string.repeat.

// Solution, join an array. No need for recursion or dp. Note that this refers to the string itself, not the boxed object, I'm not sure the full details on how this works.

/**
 * @param {number} times
 * @return {string}
 */
String.prototype.replicate = function (times) {
  const arr = new Array(times).fill(this);
  return arr.join("");
};
