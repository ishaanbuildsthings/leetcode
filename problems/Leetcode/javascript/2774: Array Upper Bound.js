// https://leetcode.com/problems/array-upper-bound/
// Difficulty: Easy

// Problem
// Write code that enhances all arrays such that you can call the upperBound() method on any array and it will return the last index of a given target number. nums is a sorted ascending array of numbers that may contain duplicates. If the target number is not found in the array, return -1.

// Solution, binary search on that number, O(log n) time, O(1) space
/**
 * @param {number} target
 * @return {number}
 */
Array.prototype.upperBound = function (target) {
  let l = 0;
  let r = this.length - 1;
  while (l < r) {
    const m = Math.ceil((r + l) / 2);
    const num = this[m];
    if (num <= target) {
      l = m;
    } else {
      r = m - 1;
    }
  }
  if (this[r] === target) {
    return r;
  }
  return -1;
};

// [3,4,5].upperBound(5); // 2
// [1,4,5].upperBound(2); // -1
// [3,4,6,6,6,6,7].upperBound(6) // 5
