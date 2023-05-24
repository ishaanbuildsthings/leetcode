// https://leetcode.com/problems/sum-of-subarray-ranges/description/
// Difficulty: Medium
// tags: monotonic stack

// Problem
/*
You are given an integer array nums. The range of a subarray of nums is the difference between the largest and smallest element in the subarray.

Return the sum of all subarray ranges of nums.
*/

// Solution, O(n) time and O(n) space
/*
Maintain a montonic stack to determine the range an element is the minimum and maximum in. The sum of ranges is just the sum of the maxes minus the sum of the mins. Store indicies in the stack and lookup the numbers inside the loops, instead of storing tuples. Assign left and right to indicate where the popped element gets bottlenecked. Iterate one extra time to do a cleanup and add a condition in the while loop.
 */

var subArrayRanges = function (nums) {
  let totalSum = 0;
  let stack = []; // holds indices of numbers, whenever we get a new number we compare it, if it is smaller, we found a bottleneck
  for (let i = 0; i < nums.length + 1; i++) {
    // we find a smaller number or we need to clean up the stack at the end
    while (
      stack.length > 0 &&
      (nums[i] < nums[stack[stack.length - 1]] || i === nums.length)
    ) {
      // mid = index of the number we pop, right = bottlneck, left = bottleneck
      const mid = stack.pop();
      const left = stack.length === 0 ? -1 : stack[stack.length - 1];
      const right = i;
      totalSum -= nums[mid] * (right - mid) * (mid - left);
    }
    stack.push(i);
  }

  stack = []; // maintain a monotonically decreasing (by the lookup of the indices) stack, whenever we see a bigger number, the bigger number is bottlenecked by the left, so pop from the stack until it is decreasing

  for (let i = 0; i < nums.length + 1; i++) {
    while (
      stack.length > 0 &&
      (nums[i] > nums[stack[stack.length - 1]] || i === nums.length)
    ) {
      const mid = stack.pop();
      const right = i;
      const left = stack.length === 0 ? -1 : stack[stack.length - 1];
      totalSum += nums[mid] * (right - mid) * (mid - left);
    }
    stack.push(i);
  }

  return totalSum;
};
