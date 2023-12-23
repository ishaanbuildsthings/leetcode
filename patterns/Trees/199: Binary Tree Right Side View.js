// https://leetcode.com/problems/binary-tree-right-side-view/description/
// Difficulty: Medium
// tags: bfs

// Problem
/*
Given the root of a binary tree, imagine yourself standing on the right side of it, return the values of the nodes you can see ordered from top to bottom.
*/

// Solution, O(n) time and O(n) space, as the deque can hold up to all the leaf nodes. Simple BFS traversal and grab the last element of each level.

var rightSideView = function (root) {
  if (!root) {
    return [];
  }

  const result = [];

  const deque = [root]; // pretend O(1) shift

  while (deque.length > 0) {
    const length = deque.length;
    for (let i = 0; i < length; i++) {
      const node = deque.shift();
      // grab the last element from every row
      if (i === length - 1) {
        result.push(node.val);
      }

      if (node.left) {
        deque.push(node.left);
      }
      if (node.right) {
        deque.push(node.right);
      }
    }
  }

  return result;
};
