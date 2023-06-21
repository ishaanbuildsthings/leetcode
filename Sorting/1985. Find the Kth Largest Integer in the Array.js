// https://leetcode.com/problems/find-the-kth-largest-integer-in-the-array/description/
// Difficulty: Medium
// tags: quickselect

// Problem
/*
NOTE: the length of the numbers can be up to 100 digits.

Input: nums = ["3","6","7","10"], k = 4
Output: "3"
Explanation:
The numbers in nums sorted in non-decreasing order are ["3","6","7","10"].
The 4th largest integer in nums is "3".


You are given an array of strings nums and an integer k. Each string in nums represents an integer without leading zeros.

Return the string that represents the kth largest integer in nums.

Note: Duplicate numbers should be counted distinctly. For example, if nums is ["1","2","2"], "2" is the first largest integer, "2" is the second-largest integer, and "1" is the third-largest integer.
*/

// Solution, O(n * m) time on average, where n is the number of strings and m is the length of the strings. O(n^2 * m) time in the worst case. O(1) space. Iterative quickselect! See 215: Kth Largest Element in Array for other solutions (heaps) and a recursive quickselect. This is a pretty straightforward one, we pick a random pivot, put that pivot at the end so it is easy to partition, then move smaller elements to the left. We use a custom comparator function to compare the strings.

var kthLargestNumber = function (nums, k) {
  const requiredIndex = nums.length - k;
  let l = 0;
  let r = nums.length - 1;

  while (true) {
    // diffs starting from l should range from 0 to rangeLength - 1. so if our numbers are 1, 3, 2. we should consider 1 (diff of 0), 3 (diff of 1), or 2 (diff of 2).
    const searchRangeLength = r - l + 1;
    const diff = Math.floor(Math.random() * searchRangeLength);
    const randomIndex = l + diff;
    const pivot = nums[randomIndex];

    [nums[r], nums[randomIndex]] = [nums[randomIndex], nums[r]];
    let insertionPointer = l;

    // do the "move zeroes" thing to move numbers <= pivot to the front of the array
    for (let i = l; i < r; i++) {
      if (compareStrings(nums[i], pivot)) {
        const temp = nums[i];
        nums[i] = nums[insertionPointer];
        nums[insertionPointer] = temp;
        insertionPointer++;
      }
    }

    // put the pivot back in the middle
    const temp = nums[insertionPointer];
    nums[insertionPointer] = nums[r];
    nums[r] = temp;

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

// returns s1 <= s2
function compareStrings(s1, s2) {
  if (s1.length < s2.length) {
    return true;
  }

  if (s1.length > s2.length) {
    return false;
  }
  /* here, the strings are the same length */

  for (let i = 0; i < s1.length; i++) {
    const digit1 = Number(s1[i]);
    const digit2 = Number(s2[i]);

    if (digit1 < digit2) {
      return true;
    }

    if (digit1 > digit2) {
      return false;
    }
  }

  return true; // if the numbers are the exact same
}
