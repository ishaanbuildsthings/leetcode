// https://leetcode.com/problems/find-minimum-in-rotated-sorted-array/
// Difficulty: Medium

// There are two portions to the rotated sorted array. The left and right portion, separated by the rotation point. All numbers in the left portion are bigger than all numbers in the right portion. If we pick the middle number, m, we are either in the left or the right portion. If we are in the left portion, m will be greater than the rightmost number. If we are in the right portion, m will be smaller than the rightmost number. We move to the relevant portion based on these results, until we find the pivot point which is the minimum.
// The left and right pointers indicate the current bounds of valid numbers we are still searching. Therefore, if l===r, there is only one potential number left, and we can return that number. If we need to move to the right, that means m was in the left portion. So l=m+1, because we don't even need to consider m. But if we move to the left, that means m was in the right portion, which is correct, so we still need to consider m, therefore r=m.

const findMin = function (nums) {
  let l = 0;
  let r = nums.length - 1;
  let m = Math.floor((r + l) / 2); // initialize it in case the array is length 1 to start

  while (l < r) {
    m = Math.floor((r + l) / 2); // push to the left for even lengths

    // if the middle number is bigger than the rightmost number, we are in the left portion, and need to search right
    if (nums[m] > nums[nums.length - 1]) {
      l = m + 1;
    }
    // otherwise, we need to search to the left
    else {
      r = m;
    }
  }
  return nums[l];
};
