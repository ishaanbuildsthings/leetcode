// https://leetcode.com/problems/search-in-rotated-sorted-array/
// Difficulty: Medium
// tags: binary search
// helper: helped by: 704: binary search

// Solution O(log n) time and O(1) space
// First we find the pivot point / minimum number in the array in log n time, using a two pointer method by checking if the middle pointer is in the left portion or right portion, the moving the left and right pointers appropriately. Once we have the pivot point, we check which side the target is on, and we get new pointers specific to one of the two portions. Then we do a simple binary search within that ascending portion to either find the target or return -1.

const search = function (nums, target) {
  // initialize pointers to locate the pivot point in log n time
  let l = 0;
  let r = nums.length - 1;
  let m = Math.floor((l + r) / 2);
  // find the pivot point
  while (l < r) {
    m = Math.floor((l + r) / 2);
    // if our number is bigger than the rightmost number, we are in the left portion, and need to search right, consider m+1 to r
    if (nums[m] > nums[nums.length - 1]) {
      l = m + 1;
    }
    // if our number is smaller than the rightmost number, or equal to it, we are in the right portion, and need to search left, consider l to m
    else {
      r = m;
    }
  }

  const pivot = l;

  // assign new pointers based on which side the target is
  if (target >= nums[0]) {
    // left side or sorted array
    if (pivot === 0) {
      // edge case where we are at a normal sorted array, the pivot is the leftmost
      r = nums.length - 1;
    } else {
      r = pivot - 1;
    }
    l = 0;
  }
  // right side
  else {
    l = pivot;
    r = nums.length - 1;
  }

  // do another binary search within the specific side
  while (l < r) {
    m = Math.floor((l + r) / 2);
    // if our number is too big, or equal to the target, we want to consider from l to m
    if (nums[m] >= target) {
      r = m;
    }
    // if our number is too small, we want to consider from m+1 to r
    else {
      l = m + 1;
    }
  }

  // return the found value or -1
  if (nums[l] === target) {
    return l;
  }
  return -1;
};
