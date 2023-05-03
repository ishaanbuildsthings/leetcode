// https://leetcode.com/problems/contains-duplicate-ii/description/
// Difficulty: Easy
// tags: sliding window fixed

// Solution
// O(n) time and O(n) space. Create a mapping that maps if a number is currently in the fixed sliding window. We don't need to worry about quantity, since if we ever reach quantity two, we could just immediately return true. Iterate over the array with a fixed window and update the mapping.

var containsNearbyDuplicate = function (nums, k) {
  const windowWidth = k + 1; // fix weird indexing
  const windowWidthFinal = Math.min(windowWidth, nums.length); // reduce window if it is bigger than the array
  const mapping = {}; // maps numbers to if they're currently in the window
  let l = 0;
  let r = windowWidthFinal - 1;

  while (r < nums.length) {
    // if this is our first iteration, populate the mapping
    if (l === 0) {
      for (let i = 0; i < windowWidthFinal; i++) {
        if (mapping[nums[i]]) {
          return true;
        } else {
          mapping[nums[i]] = true;
        }
      }
    }
    // we increment the left pointer, removing its value
    mapping[nums[l]] = false;
    l++;
    // we increment the right pointer, adding its value and seeing if it is in the window
    r++;
    if (mapping[nums[r]]) {
      return true;
    } else {
      mapping[nums[r]] = true;
    }
  }
  return false;
};
