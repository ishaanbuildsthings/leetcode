// https://leetcode.com/problems/minimum-depth-of-binary-tree/description/
// Difficulty: Easy
// tags: dfs, binary tree

// Problem
/*
Given a binary tree, find its minimum depth.

The minimum depth is the number of nodes along the shortest path from the root node down to the nearest leaf node.

Note: A leaf is a node with no children.
*/

// Solution, O(n) time, O(n) (height) space. Check the depths of the left and right, validate differently, i.e. we need both nodes to take the minimum.

var minDepth = function (root) {
  // edge case in case the initial root is null
  if (!root) {
    return 0;
  }

  // if we are a leaf node, return 1
  if (!root.left && !root.right) {
    return 1;
  }

  // if we just have a left node, return the depth of that
  else if (root.left && !root.right) {
    return 1 + minDepth(root.left);
  }

  // if we just have a right node, return that depth
  else if (root.right && !root.left) {
    return 1 + minDepth(root.right);
  }

  return 1 + Math.min(minDepth(root.left), minDepth(root.right));
};
