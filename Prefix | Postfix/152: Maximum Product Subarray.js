// https://leetcode.com/problems/maximum-product-subarray/
// Difficulty: Medium
// tags: prefix

// Solution 1
// O(n) time and O(1) space

// MODIFICATIONS:
// You could also do this slightly more concisely, by not using the current>0 or current<0 checks. Instead, just set dpMin and dpMax to be the Math.max or Math.min of three values.

// This solution tracks the minimum and maximum possible values that can be reached at a given index. Since we only need to know the previous index's values, we can use constant storage and storage these values in `dpMin` and `dpMax`. We don't need to reset dpMin and dpMax because we can ignore them later, for instance: [-2, 3]. When we are solving for 3, our max is either -2*3, or just the current index, which "clears" out the previous values / doesn't consider them.

const maxProduct = function (nums) {
  // return value
  let maxProduct = nums[0];
  let dpMin = nums[0];
  let dpMax = nums[0];

  // store the memos and compute new values
  for (let i = 1; i < nums.length; i++) {
    const current = nums[i];
    if (current > 0) {
      dpMin = Math.min(current, dpMin * current);
      dpMax = Math.max(current, dpMax * current);
    } else if (current === 0) {
      dpMin = 0;
      dpMax = 0;
    } else if (current < 0) {
      const tmp = dpMin;
      dpMin = Math.min(current, dpMax * current);
      dpMax = Math.max(current, tmp * current);
    }
    maxProduct = Math.max(maxProduct, dpMax);
  }
  return maxProduct;
};

// Solution 2 for LEARNING PURPOSES - inefficient storage use
// O(n) time and O(n) space

// This solution creates a memo mapping which stores a numbers smallest possible value and largest possible value. For instance [2, -3] The smallest and largest values for 2 are both 2. At -3, the smallest value is -6 (2*-3) and the largest value is (-3). At a 0, the values reset to 0. We store the smallest and largest values because if a number is positive, our new possible largest is the current number times that previous positive number. If a number is negative, our new possible largest is the current number times that previous smallest number, etc.

var maxProduct2 = function (nums) {
  // return value
  let maxProduct = nums[0];

  // create the memo that maps [max, min] for a given index, { 1 : [5, -3], 2 : [6, -3] }
  const memo = {};
  for (let i = 0; i < nums.length; i++) {
    memo[i] = [];
  }
  memo[0][0] = nums[0];
  memo[0][1] = nums[0];

  // store the memos and compute new values
  for (let i = 1; i < nums.length; i++) {
    const prevMax = memo[i - 1][0];
    const prevMin = memo[i - 1][1];
    const current = nums[i];
    if (current > 0) {
      // assign new max
      memo[i][0] = Math.max(current, prevMax * current);
      // assign new min
      memo[i][1] = Math.min(current, prevMin * current);
    }
    if (current === 0) {
      memo[i][0] = 0;
      memo[i][1] = 0;
    }
    if (current < 0) {
      // assign new max
      memo[i][0] = Math.max(current, prevMin * current);
      // assign new min
      memo[i][1] = Math.min(current, prevMax * current);
    }
    maxProduct = Math.max(maxProduct, memo[i][0]);
  }
  console.log(memo);
  console.log(maxProduct);
  return maxProduct;
};
