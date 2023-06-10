// https://leetcode.com/problems/subsets-ii/description/
// Difficulty: Medium
// tags: backtracking

// Problem
/*
Simplified:
Input: nums = [1,2,2]
Output: [[],[1],[1,2],[1,2,2],[2],[2,2]]

Detailed:
Given an integer array nums that may contain duplicates, return all possible
subsets
 (the power set).

The solution set must not contain duplicate subsets. Return the solution in any order.
*/

// Solution 1
// O(n log n + n*2^n) time, which reduces to n*2^n. O(n) space for the recursive callstack.
/*
Sort the numbers, so we get something like [1, 2, 2]

Then, start backtracking. We can either choose to keep a number, or skip it. If we skip a number, we must therefore skip all of that number.

If we ever reach out of bounds, we have considered all numbers, and can serialize our result (O(n) time) and add it.

Since at the worsst case we have n candidates, we can make 2^n possible subsets, and we iterate through all of these cases.
*/

var subsetsWithDup = function (nums) {
  nums.sort((a, b) => a - b);

  const result = [];

  function backtrack(currentNums, i) {
    // if we have no more numbers to consider, add the result and terminate
    if (i === nums.length) {
      result.push(JSON.parse(JSON.stringify(currentNums)));
      return;
    }

    // we decide to keep the current number
    currentNums.push(nums[i]);
    backtrack(currentNums, i + 1);
    currentNums.pop();

    // if we skip a number, we should skip all of that type, use j to find the first different number
    let j;
    for (j = i; j < nums.length; j++) {
      if (nums[j] !== nums[i]) {
        break;
      }
    }

    backtrack(currentNums, j);
  }

  backtrack([], 0);

  return result;
};
