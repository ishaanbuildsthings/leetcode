// https://leetcode.com/problems/chunk-array/description/
// Difficulty: Easy

// Problem
// Given an array arr and a chunk size size, return a chunked array. A chunked array contains the original elements in arr, but consists of subarrays each of length size. The length of the last subarray may be less than size if arr.length is not evenly divisible by size.

// You may assume the array is the output of JSON.parse. In other words, it is valid JSON.

// Please solve it without using lodash's _.chunk function.

// Solution, O(n) time and O(1) auxillary space

/**
 * @param {Array} arr
 * @param {number} size
 * @return {Array}
 */
var chunk = function (arr, size) {
  const res = [];
  let chunk = [];
  for (const e of arr) {
    chunk.push(e);
    if (chunk.length === size) {
      res.push(chunk);
      chunk = [];
    }
  }
  if (chunk.length) {
    res.push(chunk);
  }
  return res;
};
