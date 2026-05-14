// https://leetcode.com/problems/minimum-swaps-to-make-sequences-increasing/description/
// difficulty: hard
// tags: dynamic programming 1d

// Problem
/*
You are given two integer arrays of the same length nums1 and nums2. In one operation, you are allowed to swap nums1[i] with nums2[i].

For example, if nums1 = [1,2,3,8], and nums2 = [5,6,7,4], you can swap the element at i = 3 to obtain nums1 = [1,2,3,4] and nums2 = [5,6,7,8].
Return the minimum number of needed operations to make nums1 and nums2 strictly increasing. The test cases are generated so that the given input always makes it possible.

An array arr is strictly increasing if and only if arr[0] < arr[1] < arr[2] < ... < arr[arr.length - 1].
*/

// Solution, O(n) time, O(1) space
/*
It's given the array has an answer. This also means all arrays [l:] have an answer. Since [l:] doesn't depend on the prior indices. Therefore, for each index, we can track our best performance (min swaps needed) if we needed to swap and if we didn't need to swap (working backwards).
*/

var minSwap = function (nums1, nums2) {
  let priorWays = [[Infinity, Infinity, 0]]; // stores up to two tuples of [num1, num2, # swaps]

  for (let i = nums1.length - 1; i >= 0; i--) {
    const newWays = [];

    let ifDontSwap = [Infinity, Infinity, Infinity];
    let ifDoSwap = [Infinity, Infinity, Infinity];
    let ifDontSwapFound = false; // helps us determine if we have valid ways of when we swap/dont swap
    let ifDoSwapFound = false;

    // check up to two prior ways
    for (const way of priorWays) {
      const [num1Head, num2Head, numSwaps] = way;
      // if we don't swap
      if (nums1[i] < num1Head && nums2[i] < num2Head) {
        const newIfDontSwap = [nums1[i], nums2[i], numSwaps];
        // when we don't swap, if we can get fewer total swaps than any other time when we don't swap, do so
        if (newIfDontSwap[2] < ifDontSwap[2]) {
          ifDontSwap = newIfDontSwap;
          ifDontSwapFound = true;
        }
      }
      // if we do swap
      if (nums1[i] < num2Head && nums2[i] < num1Head) {
        const newIfDoSwap = [nums2[i], nums1[i], numSwaps + 1];
        if (newIfDoSwap[2] < ifDoSwap[2]) {
          ifDoSwap = newIfDoSwap;
          ifDoSwapFound = true;
        }
      }
    }

    if (ifDontSwapFound) {
      newWays.push(ifDontSwap);
    }
    if (ifDoSwapFound) {
      newWays.push(ifDoSwap);
    }

    priorWays = newWays;
  }

  let result = Infinity;
  // check up to both possible ways (we swapped or didn't swap the first two elements)
  for (const priorWay of priorWays) {
    result = Math.min(result, priorWay[2]);
  }
  return result;
};

/*
4 7 = no swaps
7 4 = 1 swap

5 3 = 1 swap


*/
