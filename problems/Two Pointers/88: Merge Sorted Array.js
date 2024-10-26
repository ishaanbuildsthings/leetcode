// https://leetcode.com/problems/merge-sorted-array/description/
// Difficulty: Easy
// tags: two pointers, array

// Problem
/*
Simplified:
Input: nums1 = [1,2,3,0,0,0], m = 3, nums2 = [2,5,6], n = 3
Output: [1,2,2,3,5,6]
Explanation: The arrays we are merging are [1,2,3] and [2,5,6].
The result of the merge is [1,2,2,3,5,6] with the underlined elements coming from nums1.

Detailed:
You are given two integer arrays nums1 and nums2, sorted in non-decreasing order, and two integers m and n, representing the number of elements in nums1 and nums2 respectively.

Merge nums1 and nums2 into a single array sorted in non-decreasing order.

The final sorted array should not be returned by the function, but instead be stored inside the array nums1. To accommodate this, nums1 has a length of m + n, where the first m elements denote the elements that should be merged, and the last n elements are set to 0 and should be ignored. nums2 has a length of n.
*/

// Solution, m + n time, O(1) space
/*
Fill in nums1 backwards. Track an insertion pointer, and a pointer for the number of nums1 and nums2. Take the bigger number and insert it.

We could also duplicate the first m numbers into the empty spots in nums1, then iterate forwards starting from that duplicated portion.
*/

var merge = function (nums1, m, nums2, n) {
  // tracks the numbers we are handling for nums1 and nums2
  let p1 = m - 1;
  let p2 = n - 1;

  // iterate backwards starting from the end of nums1. we compare the two numbers at p1 and p2, and insert the biggest one
  for (
    let insertionPointer = nums1.length - 1;
    insertionPointer >= 0;
    insertionPointer--
  ) {
    const number1 = nums1[p1];
    const number2 = nums2[p2];

    if (number1 >= number2) {
      nums1[insertionPointer] = number1;
      p1--;
    }
    // p2 < 0 means it went bounds, which happens when all numbers from nums2 are used
    else if (p2 < 0) {
      nums1[insertionPointer] = number1;
      p1--;
    }
    // either p1 went out of bounds, or number1 was smaller than number2
    else {
      nums1[insertionPointer] = number2;
      p2--;
    }
  }
};
