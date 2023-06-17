// https://leetcode.com/problems/sum-of-left-leaves/description/
// Difficulty: Easy
// tags: dfs, binary tree

// Problem
/*
Given the root of a binary tree, return the sum of all left leaves.

A leaf is a node with no children. A left leaf is a leaf that is the left child of another node.
*/

// Solution, O(n) time and O(n) (height) space. Just pass in the direction of the parent.

var sumOfLeftLeaves = function (root) {
  let sum = 0;

  // calledFrom right means we are a left child
  function dfs(node, calledFrom) {
    if (!node) {
      return;
    }

    // if we are a leaf
    if (!node.left && !node.right && calledFrom === "right") {
      sum += node.val;
      return;
    }

    dfs(node.left, "right");
    dfs(node.right, "left");
  }

  dfs(root, "left");

  return sum;
};
