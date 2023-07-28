// https://leetcode.com/problems/binary-tree-level-order-traversal-ii/description/
// difficulty: Medium
// tags: binary tree, BFS

// Problem
/*
Given the root of a binary tree, return the bottom-up level order traversal of its nodes' values. (i.e., from left to right, level by level from leaf to root).
*/

// Solution, O(n) time (with a real queue), O(n) (width) space.
/*
Store each row in a BFS, then reverse the order of the rows.
*/

var levelOrderBottom = function (root) {
  // edge case or the BFS doesn't run
  if (!root) {
    return [];
  }

  const queue = [root]; // fake queue

  const traversal = [];

  while (queue.length > 0) {
    const row = [];
    const length = queue.length;
    for (let i = 0; i < length; i++) {
      const node = queue.shift();
      row.push(node.val);
      if (node.left) {
        queue.push(node.left);
      }
      if (node.right) {
        queue.push(node.right);
      }
    }
    traversal.push(row);
  }

  return traversal.reverse();
};
