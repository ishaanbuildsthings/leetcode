// https://leetcode.com/problems/dot-product-of-two-sparse-vectors/description/
// difficulty: Medium
// tags: Two Pointers

// Problem
/*
Given two sparse vectors, compute their dot product.

Implement class SparseVector:

SparseVector(nums) Initializes the object with the vector nums
dotProduct(vec) Compute the dot product between the instance of SparseVector and vec
A sparse vector is a vector that has mostly zero values, you should store the sparse vector efficiently and compute the dot product between two SparseVector.

Follow up: What if only one of the vectors is sparse?
*/

// Solution, O(n) time to initialize, O(min(n, m)) time to get dot product
/*
We only need to store the non-zero values, so do that in a constructor, including the relevant index.

When doing the dot product, maintain two pointers. Iterate the first pointer whenever it is less than the second. If the pointers meet, add to the result, and iterate both.
*/

/**
 * @param {number[]} nums
 * @return {SparseVector}
 */
var SparseVector = function (nums) {
  this.nonZeroes = []; // stores [index, num]
  for (let i = 0; i < nums.length; i++) {
    if (nums[i] !== 0) {
      this.nonZeroes.push([i, nums[i]]);
    }
  }
};

// Return the dotProduct of two sparse vectors
/**
 * @param {SparseVector} vec
 * @return {number}
 */
SparseVector.prototype.dotProduct = function (vec) {
  let p1 = 0; // points to nonZeroes array
  let p2 = 0; // points to vec nonZeroes array

  let result = 0;

  // increment until one pointer is out of bounds (at that point we could never add to our dot product)
  while (p1 < this.nonZeroes.length && p2 < vec.nonZeroes.length) {
    // while the p1 index is < the p2 index - 1 (so we never go out of bounds), we iterate, stopping in the best case where the indices are equal.
    while (
      p1 < this.nonZeroes.length - 1 &&
      this.nonZeroes[p1][0] < vec.nonZeroes[p2][0]
    ) {
      p1++;
    }

    // if the indicies met, we can add their results
    if (vec.nonZeroes[p2][0] === this.nonZeroes[p1][0]) {
      result += this.nonZeroes[p1][1] * vec.nonZeroes[p2][1];
      p1++;
      p2++;
      continue;
    }

    p2++;
  }

  return result;
};

// Your SparseVector object will be instantiated and called as such:
// let v1 = new SparseVector(nums1);
// let v2 = new SparseVector(nums2);
// let ans = v1.dotProduct(v2);
