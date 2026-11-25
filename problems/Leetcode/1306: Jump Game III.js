// https://leetcode.com/problems/jump-game-iii/description/
// Difficulty: Medium
// Tags: Graphs, matrix dfs

// Problem
/*
Given an array of non-negative integers arr, you are initially positioned at start index of the array. When you are at index i, you can jump to i + arr[i] or i - arr[i], check if you can reach any index with value 0.

Notice that you can not jump outside of the array at any time.
*/

// Solution, O(n) time and O(n) space
/*
We can simply run a dfs from our cell. visited neighbor cells. This question is literally just given a graph, see if there is a 0. So we iterate through all nodes. We maintain a seen set to not duplicate visits.
*/

var canReach = function (arr, start) {
  const seen = new Set(); // holds indices of cells we have visited

  function dfs(i) {
    // base case, we are at a 0
    if (arr[i] === 0) {
      return true;
    }

    seen.add(i);

    const leftJumpIndex = i - arr[i];
    const rightJumpIndex = i + arr[i];

    if (!seen.has(leftJumpIndex)) {
      if (dfs(leftJumpIndex)) {
        return true;
      }
    }

    if (!seen.has(rightJumpIndex)) {
      if (dfs(rightJumpIndex)) {
        return true;
      }
    }

    return false;
  }

  return dfs(start);
};
