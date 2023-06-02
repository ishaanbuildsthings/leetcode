// https://leetcode.com/problems/binary-tree-postorder-traversal/description/
// Difficulty: Easy
// tags: binary tree, postorder traversal

// Problem
/*
Given the root of a binary tree, return the postorder traversal of its nodes' values.
*/

// Solution 1, recursive, O(n) time, O(n) space
/*
Whenenever we see a node, DFS down to the left. Eventually we will hit null, then stop that context. Then DFS down to the right, hitting null again. After that, add the node's value to the result.
*/

var postorderTraversal = function (root) {
  const result = [];

  function dfs(node) {
    if (!node) return;

    dfs(node.left);
    dfs(node.right);
    result.push(node.val);
  }

  dfs(root);

  return result;
};

// Solution 2, iterative, O(n) time, O(n) space
