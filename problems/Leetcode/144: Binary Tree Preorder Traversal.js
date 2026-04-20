// https://leetcode.com/problems/binary-tree-preorder-traversal/description/
// Difficulty: Easy
// tags: binary tree, preorder traversal

// Problem
/*
Given the root of a binary tree, return the preorder traversal of its nodes' values.
*/

// Solution 1, recursive, O(n) time and O(n) space
/*
Whenever we see a node, print it. Then DFS down to the left. Once we hit null, stop that context, then start traveling right.
*/

var preorderTraversal = function (root) {
  const result = [];

  function dfs(node) {
    if (!node) return;

    result.push(node.val);
    dfs(node.left);
    dfs(node.right);
  }

  dfs(root);

  return result;
};

// Solution 2, iterative, O(n) time and O(n) space
/*
As soon as we see a node, add its value to the result. Then DFS down left a step. Eventually when we hit null, stop that execution context. Go back up to the middle node, and redirect to its right child, then continue;
*/

var preorderTraversal = function (root) {
  const result = [];

  const stack = [];
  let pointer = root;

  while (stack.length > 0 || pointer) {
    while (pointer) {
      result.push(pointer.val);
      stack.push(pointer);
      pointer = pointer.left;
    }
    /* here we hit null */

    const bottomLeftNode = stack.pop();
    pointer = bottomLeftNode.right;
  }

  return result;
};
