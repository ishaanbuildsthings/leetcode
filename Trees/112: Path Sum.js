// https://leetcode.com/problems/path-sum/description/
// Difficulty: Easy
// tags: dfs

// Problem

/*
Given the root of a binary tree and an integer targetSum, return true if the tree has a root-to-leaf path such that adding up all the values along the path equals targetSum.

A leaf is a node with no children.
*/

// Solution, O(n) time and O(n) (height) space for the callstack

/*
DFS throughout the tree, if we have the target sum and are at a leaf, return true. Otherwise return the results of either of the children.
*/

var hasPathSum = function (root, targetSum) {
  function dfs(node, currentSum) {
    if (!node) {
      return false;
    }

    currentSum += node.val;

    if (currentSum === targetSum && !node.left && !node.right) {
      return true;
    }

    return dfs(node.left, currentSum) || dfs(node.right, currentSum);
  }

  return dfs(root, 0);
};
