// https://leetcode.com/problems/product-of-array-except-self/description/
// Difficulty: Medium
// tags: prefix / postfix, dynamic programming

// Solution 1
// O(n) time and O(1) auxillary space, uses a dpPrefix and dpPostfix and iterates over the numbers in two directions, storing the multiplied results in the output array.

const productExceptSelf = function (nums) {
  const result = [];
  let dpPrefix = 1;
  for (const num of nums) {
    result.push(dpPrefix);
    dpPrefix *= num;
  }

  let dpPostfix = 1;
  for (let i = nums.length - 1; i >= 0; i--) {
    result[i] *= dpPostfix;
    dpPostfix *= nums[i];
  }
  return result;
};

// Solution 2
// O(n) time and O(n) auxillary space. Creates an array of products before the given number, an array of products after the given number, and multiplies them together to form the final array:

const productExceptSelf2 = function (nums) {
  const productsBefore = [1];
  for (let i = 1; i < nums.length; i++) {
    productsBefore[i] = productsBefore[i - 1] * nums[i - 1];
  }

  const productsAfter = new Array(nums.length);
  productsAfter[nums.length - 1] = 1;
  for (let i = nums.length - 2; i >= 0; i--) {
    productsAfter[i] = productsAfter[i + 1] * nums[i + 1];
  }

  const productsExceptSelf = [];
  for (let i = 0; i < nums.length; i++) {
    productsExceptSelf[i] = productsBefore[i] * productsAfter[i];
  }

  return productsExceptSelf;
};
