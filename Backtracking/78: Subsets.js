// https://leetcode.com/problems/subsets/description/
// Difficulty: Medium
// tags: backtracking

// Solution
// O(n * 2^n) time. 2^n if we draw out the decision graph. We multiply by n since each result requires serialization of time n.
// O(n) space, for the recursive callstack.
/*
For each number, we either skip it or add it. Once we terminate (we've made a decision on all numbers), we update the result. Make sure to pop the element off after we have considered it.
*/

var subsets = function (nums) {
  const result = [];

  function backtrack(currentNums, i) {
    // we cannot recurse more if we have used all number types and moved on
    if (i === nums.length) {
      result.push(JSON.parse(JSON.stringify(currentNums)));
      return;
    }

    currentNums.push(nums[i]);
    backtrack(currentNums, i + 1);
    currentNums.pop();

    backtrack(currentNums, i + 1);
  }

  backtrack([], 0);

  return result;
};
