// https://leetcode.com/problems/count-good-nodes-in-binary-tree/description/
// Difficulty: Medium
// tags: dfs

// Problem
/*
Given a binary tree root, a node X in the tree is named good if in the path from root to X there are no nodes with a value greater than X.

Return the number of good nodes in the binary tree.
*/

// Solution, O(n) (nodes) time and O(n) (height) space. Recurse through the tree maintaining prior seen maxes.

var goodNodes = function (root) {
  let result = 0;

  // iterates over the tree in a dfs, maintaining the max prior seen number
  function dfs(node, maxPrevious) {
    if (!node) {
      return;
    }

    let newMax = maxPrevious;
    if (node.val >= maxPrevious) {
      result += 1;
      newMax = node.val;
    }

    dfs(node.left, newMax);
    dfs(node.right, newMax);
  }

  dfs(root, -Infinity);

  return result;
};
