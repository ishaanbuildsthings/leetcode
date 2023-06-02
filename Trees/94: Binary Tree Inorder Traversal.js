// https://leetcode.com/problems/binary-tree-inorder-traversal/description/
// Difficulty: Easy
// tags: binary tree, inorder traversal

// Problem
/*
Given the root of a binary tree, return the inorder traversal of its nodes' values.
*/

// Solution 1, recursive, O(n) time and O(n) space
/*
DFS down to the left. Once we reach null, stop that execution context. Print the value, then dfs to the right.
*/

var inorderTraversal = function (root) {
  const result = [];

  function dfs(node) {
    if (!node) return;

    dfs(node.left);
    result.push(node.val);
    dfs(node.right);
  }

  dfs(root);

  return result;
};

// Solution 2, iterative, O(n) time and O(n) space
/*
Use a stack to maintain a stack-trace sort of. Whenever we see a node, add it to the stack, and travel left. Eventually we will reach null. When we do, print the top element from the stack. Then start traveling to the right of that element. We can think of the inorder traversal as basically a node with two null children. First we put the node onto the stack, then we go to the left null, have nothing there, we print the node, then go to the right. Once again we have null, so we would go back to the stack, which would print the even higher element.
*/

var inorderTraversal = function (root) {
  const result = [];

  const stack = []; // represents nodes that have been seen, but we cannot add them to results until their left children are done, kind of like the 'stack trace' that maintains info for us and lets us go back up
  let pointer = root; // represents where we are

  while (stack.length > 0 || pointer) {
    // keep descending left, adding nodes until we hit null
    while (pointer) {
      stack.push(pointer);
      pointer = pointer.left;
    }
    /* here we hit null */

    /*
        once we hit null, we cannot go any more left. now we can pop up, print that value, then go right
        */

    const bottomLeftNode = stack.pop();
    result.push(bottomLeftNode.val);

    pointer = bottomLeftNode.right;
  }

  return result;
};
