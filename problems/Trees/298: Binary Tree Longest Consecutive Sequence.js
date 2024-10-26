// https://leetcode.com/problems/binary-tree-longest-consecutive-sequence/description/
// Difficulty: Medium
// Tags: binary tree

// Problem
/*
Given the root of a binary tree, return the length of the longest consecutive sequence path.

A consecutive sequence path is a path where the values increase by one along the path.

Note that the path can start at any node in the tree, and you cannot go from a node to its parent in the path.
*/

// Solution, O(n) time, O(height) space, just check the value of the node below it, and its current sequence path, update a global variable as needed

var longestConsecutive = function (root) {
  let result = 0;

  // from each node, we need to know the value of the node below it, and its current longest sequence path
  function dfs(node) {
    if (!node) {
      return 0;
    }

    const leftCurrentLongestPath = dfs(node.left);
    const rightCurrentLongestPath = dfs(node.right);

    let currentLongestPath = 1; // defaults to just the node's value itself

    if (node.left && node.left.val === node.val + 1) {
      currentLongestPath = 1 + leftCurrentLongestPath;
    }

    if (node.right && node.right.val === node.val + 1) {
      currentLongestPath = Math.max(
        currentLongestPath,
        1 + rightCurrentLongestPath
      );
    }

    result = Math.max(result, currentLongestPath);

    return currentLongestPath;
  }

  dfs(root);

  return result;
};
