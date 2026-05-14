// https://leetcode.com/problems/combination-sum/description/
// Difficulty: Medium
// tags: backtracking

// Problem
/*
Simplified:
Input: candidates = [2,3,6,7], target = 7
Output: [[2,2,3],[7]]
Explanation:
2 and 3 are candidates, and 2 + 2 + 3 = 7. Note that 2 can be used multiple times.
7 is a candidate, and 7 = 7.
These are the only two combinations.

Detailed:
Given an array of distinct integers candidates and a target integer target, return a list of all unique combinations of candidates where the chosen numbers sum to target. You may return the combinations in any order.

The same number may be chosen from candidates an unlimited number of times. Two combinations are unique if the
frequency
 of at least one of the chosen numbers is different.

The test cases are generated such that the number of unique combinations that sum up to target is less than 150 combinations for the given input.
*/

// Solution
/*
Maintain a stack of elements we have currently added, and a sum and an index of the leftmost element we are allowed to use. For the given recursive call, try multiple calls, starting from the leftmost element of candidates, until the end. Our base cases end when our sum is >= target. After we try a case, we need to pop that number off the stack as we are reusing the array.
*/

var combinationSum = function (candidates, target) {
  const result = [];
  // allowed index us the leftmost index we are allowed to use from candidates
  function dfs(currArr, currSum, allowedIndex) {
    if (currSum > target) {
      return;
    }

    if (currSum === target) {
      const validAnswer = JSON.parse(JSON.stringify(currArr));
      result.push(validAnswer);
      return;
    }

    for (let i = allowedIndex; i < candidates.length; i++) {
      const num = candidates[i];
      currArr.push(num);
      dfs(currArr, currSum + num, i);
      currArr.pop();
    }
  }

  dfs([], 0, 0);

  return result;
};
t;
