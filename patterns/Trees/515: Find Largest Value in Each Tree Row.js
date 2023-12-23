// https://leetcode.com/problems/find-largest-value-in-each-tree-row/description/
// Difficulty: Medium
// tags: bfs

// Problem
/*
Given the root of a binary tree, return an array of the largest value in each row of the tree (0-indexed).
*/

// Solution, bfs, O(n) time and O(n) space
/*
Do a bfs, for each row track the largest and add it. We could also do a DFS, maintaing the current depth, and update an array with the largest value at each depth.
*/
var largestValues = function (root) {
  if (!root) {
    return [];
  }

  const result = [];

  const deque = [root]; // fake deque

  while (deque.length > 0) {
    const length = deque.length;
    let largest = -Infinity;
    for (let i = 0; i < length; i++) {
      const node = deque.shift();
      if (node.val > largest) {
        largest = node.val;
      }
      if (node.left) {
        deque.push(node.left);
      }
      if (node.right) {
        deque.push(node.right);
      }
    }
    result.push(largest);
  }
  return result;
};
