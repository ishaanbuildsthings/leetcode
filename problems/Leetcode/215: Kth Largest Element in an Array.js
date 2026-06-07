// https://leetcode.com/problems/kth-largest-element-in-an-array/description/
// Difficulty: Medium
// tags: quickselect

// Problem
/*
Given an integer array nums and an integer k, return the kth largest element in the array.

Note that it is the kth largest element in the sorted order, not the kth distinct element.

You must solve it in O(n) time complexity.


Example:
Given an integer array nums and an integer k, return the kth largest element in the array.

Note that it is the kth largest element in the sorted order, not the kth distinct element.

You must solve it in O(n) time complexity.
*/

// Solution, O(n) time average case, O(n^2) time worst case. O(log n) space average, O(n) space worst, due to recursive callstack.
// * Solution 2 further below is the iterative version which is O(1) space.
// * we could also do various other, worse strategies. sorting then checking the element is n log n. heapifying then popping k elements is n + k log n. Maintaining a minheap of size k, for the largest k elements is another way. For n elements, we do log k operations, so n log k.
// * Soltuion 3 is kth largest but instead of tracking the required index, we pass the kth largest to the quick select

/*
Pick a pivot, ideally random, though I used the rightmost one as it makes it easy to do the "move zeroes" part where we move numbers <= the pivot to the left. Then, iterate through the region, moving smaller elements to the left. Replace the pivot into where it belongs at the end. Check where our pivot is relative to the required index we need, and recurse on the left or right side depending on that. If we are at the required index, return the pivot.

In the worst case, our partition doesn't reduce any elements, i.e. everything is smaller than the pivot. This would end up being n^2 iterations and a callstack depth of n. Average case splits in half each time, and therefore is n time (we only consider one half, so not n log n), and log n for the callstack depth.
*/

var findKthLargest = function (nums, k) {
  const requiredIndex = nums.length - k;
  function quickSelect(l, r) {
    const pivot = nums[r];
    // do the "move zeroes" technique where we move all smaller numbers to the front of the array
    let insertionPointer = l;
    for (let i = l; i < r; i++) {
      if (nums[i] <= pivot) {
        const temp = nums[i];
        nums[i] = nums[insertionPointer];
        nums[insertionPointer] = temp;
        insertionPointer++;
      }
    }

    const temp = nums[insertionPointer];
    nums[insertionPointer] = pivot;
    nums[r] = temp;

    if (insertionPointer === requiredIndex) {
      return pivot;
    }

    // search right
    else if (insertionPointer < requiredIndex) {
      return quickSelect(insertionPointer + 1, r);
    }

    // search left
    else {
      return quickSelect(l, insertionPointer - 1);
    }
  }

  return quickSelect(0, nums.length - 1);
};

// * Solution 2, iterative version using a while loop.

var findKthLargest = function (nums, k) {
  let l = 0;
  let r = nums.length - 1;
  const requiredIndex = nums.length - k;

  while (true) {
    const pivot = nums[r];
    let insertionPointer = l;
    // move smaller elements to the left of the array
    for (let i = l; i < r; i++) {
      if (nums[i] <= pivot) {
        const temp = nums[i];
        nums[i] = nums[insertionPointer];
        nums[insertionPointer] = temp;
        insertionPointer++;
      }
    }

    // move the pivot back into the middle
    const temp = nums[r];
    nums[r] = nums[insertionPointer];
    nums[insertionPointer] = temp;

    if (insertionPointer === requiredIndex) {
      return nums[insertionPointer];
    }

    // search right
    else if (insertionPointer < requiredIndex) {
      l = insertionPointer + 1;
    }

    // search left
    else {
      r = insertionPointer - 1;
    }
  }
};

// Solution 3, instead of tracking the required index, we pass the kth largest to the quick select. for instance:
/*
  0 1 2 3 4 5 6 7
      ^
      pivot   ^
      looking for the 2nd largest, but we know the pivot is the 6th largest, so we must search in the right region, still for the 2nd largest

  0 1 2 3 4 5 6 7
          ^
          pivot

  but we are looking for the 6th largest, we know that pivot is the 4th largest. so we look in the left region, for the 2nd largest
*/
var findKthLargest = function (nums, k) {
  function quickSelect(l, r, kthLargest) {
    const pivot = nums[r];
    let insertionPointer = l;
    // move all numbers <= pivot to the left side of our partition
    for (let i = l; i < r; i++) {
      if (nums[i] <= pivot) {
        const temp = nums[insertionPointer];
        nums[insertionPointer] = nums[i];
        nums[i] = temp;
        insertionPointer++;
      }
    }
    // swap the pivot back in
    const temp = nums[insertionPointer];
    nums[insertionPointer] = nums[r];
    nums[r] = temp;

    if (r - insertionPointer === kthLargest - 1) {
      return pivot;
    }
    // too many numbers on the right
    else if (r - insertionPointer > kthLargest - 1) {
      return quickSelect(insertionPointer + 1, r, kthLargest);
    }
    // too many numbers on the left
    else {
      const largeElementsDiscard = r - insertionPointer + 1; // we will toss out all numbers from the insertion pointer and higher
      const newLargest = kthLargest - largeElementsDiscard;
      return quickSelect(l, insertionPointer - 1, newLargest);
    }
  }

  return quickSelect(0, nums.length - 1, k);
};
