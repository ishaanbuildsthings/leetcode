// https://leetcode.com/problems/array-with-elements-not-equal-to-average-of-neighbors/description/
// Difficulty: Medium
// tags: sorting, bubble sort
// Problem

/*
Simplfied: You have an array of different numbers, and need to sort it so no number is the average of its two neighbors.

Detailed:
You are given a 0-indexed array nums of distinct integers. You want to rearrange the elements in the array such that every element in the rearranged array is not equal to the average of its neighbors.

More formally, the rearranged array should have the property such that for every i in the range 1 <= i < nums.length - 1, (nums[i-1] + nums[i+1]) / 2 is not equal to nums[i].

Return any rearrangement of nums that meets the requirements.
*/

// Solution 1, O(n log n) time to sort, and O(n) or O(1) memory depending on how much memory the sorting needs. But also since we return a new result array which is n concurrent memory, any extra memory during the sorting should be within that bound I believe.
/*
Sort the array, [0, 1, 2, 3, 4, 5]
If we have numbers that form peaks and valleys, like 0 5 1 4 2 3, no number can ever be the average of its neighbors, because any given number is either bigger than both its neighbors or smaller. So after sorting the array just pull from the left and right in turn. 0, 5, 1, 4, 2, 3.
*/
// * Solution 2 is an O(n) solution

var rearrangeArray = function (nums) {
  nums.sort((a, b) => a - b);
  const result = [];
  let l = 0;
  let r = nums.length - 1;
  let turnOrder = 0; // 0 starts with L
  while (result.length < nums.length) {
    if (!turnOrder) {
      result.push(nums[l]);
      l++;
      turnOrder = 1 - turnOrder;
    } else {
      result.push(nums[r]);
      r--;
      turnOrder = 1 - turnOrder;
    }
  }
  return result;
};

// Solution 2
/*
Do a bubble sort but just swap elements one time. Say we have [1, 2, 3]. 2 is the average. If we swap 2 with 3, we know that 3 can never be the new average. Because if 2 is the average it means 2 was between the other numbers, so when we swap it the new number will either be lower than both or higher than both. The problem is when we do a swap, we also swap one element backwards, which could potentially interfere with prior bubble swaps. For instance [0, 1, 2, 3, 4, 5], we swap the 1 and 2: [0, 2, 1, 3, 4, 5]. We swap the 4 and 5: [0, 2, 1, 3, 5, 4]. But now that we swapped the 5 back, the 3 becomes a new average. In order to fix this, we also have to go from the other direction and do another series of swaps, So swap 1 and 3: [0, 2, 3, 1, 5, 4]
*/
