// https://leetcode.com/problems/binary-search/
// Difficulty: Easy
// tags: binary search
// helper: helps 704: Binary Search, and 153: Find Minimum in Rotated Sorted Array

// Solution
// O(log n) time and O(1) space. Initialize two pointers and compute the middle pointer. If the middle value is too big or equal to the target, we should consider at most from l to r (inclusive), so r=m. If it's too small, we want to consider only m+1 to r. Once the pointers have collided, check if that value is what we want and return the appropriate index.
// Our pointers will always collide, even if the target isn't there, for instance: [1, 3, 5] and our target is 2. Our middle value is 3, which is >= target, so we consider [1, 3]. Our midpoint is now 1, which is smaller, so we consider [3]. Essentially the l and r indices bind a range of numbers we have not yet eliminated. Once we have only one number left, the while loop stops since l===r, and we check if that number is the target. We just keep elimintating possible numbers, "it can't be any of these" until we have one left.

const search = function (nums, target) {
  let l = 0;
  let r = nums.length - 1;
  let m = Math.floor((l + r) / 2); // errs left

  while (l < r) {
    m = Math.floor((l + r) / 2);
    if (nums[m] >= target) {
      r = m;
    } else {
      l = m + 1;
    }
  }

  if (nums[l] === target) {
    return l;
  }
  return -1;
};
