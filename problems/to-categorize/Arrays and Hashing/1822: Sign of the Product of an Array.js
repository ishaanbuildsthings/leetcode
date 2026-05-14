// https://leetcode.com/problems/sign-of-the-product-of-an-array/description/
// Difficulty: Easy

// Problem
/*
There is a function signFunc(x) that returns:

1 if x is positive.
-1 if x is negative.
0 if x is equal to 0.
You are given an integer array nums. Let product be the product of all values in the array nums.

Return signFunc(product).
*/

// Solution, O(n) time and O(1) space. Iterate, tracking negatives. If we see a 0 return immediately. Otherwise return based on the number of negatives.

var arraySign = function (nums) {
  let negCount = 0;
  for (const num of nums) {
    if (num === 0) {
      return 0;
    }
    if (num < 0) {
      negCount++;
    }
  }

  if (negCount % 2 === 1) {
    return -1;
  }

  return 1;
};
