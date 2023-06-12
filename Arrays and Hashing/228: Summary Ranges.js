// https://leetcode.com/problems/summary-ranges/description/
// Difficulty: Easy

// Problem
/*
Simplified:
Input: nums = [0,1,2,4,5,7]
Output: ["0->2","4->5","7"]
Explanation: The ranges are:
[0,2] --> "0->2"
[4,5] --> "4->5"
[7,7] --> "7"

Detailed:
You are given a sorted unique integer array nums.

A range [a,b] is the set of all integers from a to b (inclusive).

Return the smallest sorted list of ranges that cover all the numbers in the array exactly. That is, each element of nums is covered by exactly one of the ranges, and there is no integer x such that x is in one of the ranges but not in nums.

Each range [a,b] in the list should be output as:

"a->b" if a != b
"a" if a == b
*/

// Solution, O(n) time and O(1) space
/*
Iterate over the array, using two while loops. The first to track when we finish, the second to run the inner loop which accumulates the range.
*/

var summaryRanges = function (nums) {
  const result = [];

  let i = 0;
  while (i < nums.length) {
    const start = nums[i];
    let str = `${start}->`;
    let length = 1;
    while (nums[i + 1] === nums[i] + 1) {
      i++;
      length++;
    }
    // we only have one number in the range
    if (length === 1) {
      result.push(String(nums[i]));
    } else {
      str += nums[i];
      result.push(str);
    }
    i++;
  }

  return result;
};
