// https://leetcode.com/problems/product-of-array-except-self/description/
// Difficulty: Medium
// tags: prefix / postfix

// Solution 1
// O(n) time and O(n) auxillary space. Creates an array of products before the given number, an array of products after the given number, and multiplies them together to form the final array:

const productExceptSelf = function (nums) {
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

// Solution 2
// O(n) time and O(1) auxillary space, works a similar way but instead of creating separate arrays, cleverly keeps a running tally with a number

const productExceptSelf2 = function (nums) {
  const length = nums.length;
  const result = new Array(length).fill(1);

  // Calculate the product of elements before the current index
  let productBefore = 1;
  for (let i = 0; i < length; i++) {
    result[i] *= productBefore;
    productBefore *= nums[i];
  }

  // Calculate the product of elements after the current index
  let productAfter = 1;
  for (let i = length - 1; i >= 0; i--) {
    result[i] *= productAfter;
    productAfter *= nums[i];
  }

  return result;
};
