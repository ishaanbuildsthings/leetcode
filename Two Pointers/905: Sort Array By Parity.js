// https://leetcode.com/problems/sort-array-by-parity/description/
// Difficulty: Easy
// tags: two pointers

// Solution
// O(n) time and O(1) space. Create two pointers at the left and right, iterate over the array and swap the even numbers to the left and the odd numbers to the right.
// This works because we don't need to preserve relative order, if we needed to preserve relative order, like 283: Move Zeroes, we would need to start both pointers at the left

const sortArrayByParity = function (nums) {
  let l = 0; // looks for evens to throw to the right
  let r = nums.length - 1; // looks for odds to throw to the left
  while (l < r) {
    // find the next 0
    while (nums[l] % 2 === 0 && l < r) {
      l++;
    }
    // find the odd
    while (nums[r] % 2 === 1 && l < r) {
      r--;
    }
    const temp = nums[r];
    nums[r] = nums[l];
    nums[l] = temp;
  }
  return nums;
};
