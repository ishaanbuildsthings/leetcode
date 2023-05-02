// https://leetcode.com/problems/move-zeroes/description/
// Difficulty: Easy
// tags: two pointers

// Solution
// O(n) time and O(1) space. Place a pointer at the rightmost value, because we want to stop when our left pointer reaches that value. It's harder to just iterate over the array because we are modifying it in place, so tracking it with a pointer is easier.
// It's okay if the rightmost value is a 0, for instance: [1, 0, 1, 0, 0]. We still process all values up to but not including that point. It might mean we unnecessarily process some extra 0s, for instance the second 0 in that array.

const moveZeroes = function (nums) {
  let l = 0;
  let r = nums.length - 1;

  while (l < r) {
    if (nums[l] === 0) {
      nums.splice(l, 1);
      nums.push(0);
      r--;
    } else {
      l++;
    }
  }
  return nums;
};
