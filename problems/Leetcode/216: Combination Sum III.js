// https://leetcode.com/problems/combination-sum-iii/description/
// difficulty: Medium
// tags: backtracking

// Problem
/*
Find all valid combinations of k numbers that sum up to n such that the following conditions are true:

Only numbers 1 through 9 are used.
Each number is used at most once.
Return a list of all possible valid combinations. The list must not contain the same combination twice, and the combinations may be returned in any order.
*/

// Solution
/*
Typical backtracking. Each number can be used or skipped. If we meet the criteria, we spend n time adding to the result. I would have to think more about the time complexity. A naive upper bound is n*2^n, but clearly we can't truly explore to depth n, since k<<n, any time we do take a number we would immediately stop (we can also prune if proceeding would only result in invalid future states if we ever took a number). Space is O(n) as written for the callstack depth and result size.
*/

var combinationSum3 = function (k, n) {
  const result = [];
  function backtrack(currentNums, currentSum, num) {
    if (currentNums.length === k && currentSum === n) {
      result.push([...currentNums]);
      return;
    }

    // if we have k numbers but not the right sum, we stop
    if (currentNums.length === k) {
      return;
    }

    // if we considered all 1-9, we stop
    if (num === 10) {
      return;
    }

    // if we take the current number, assuming the sum would fit
    if (currentSum + num <= n) {
      currentNums.push(num);
      backtrack(currentNums, currentSum + num, num + 1);
      currentNums.pop();
    }

    // if we skip
    backtrack(currentNums, currentSum, num + 1);
  }

  backtrack([], 0, 1);

  return result;
};
