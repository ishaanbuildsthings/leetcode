// https://leetcode.com/problems/find-bottom-left-tree-value/description/
// Difficulty: Medium
// tags: bfs

// Problem
// Given the root of a binary tree, return the leftmost value in the last row of the tree.

// Solution, O(n) time and O(n) space

/*
Do a bfs, for each level grab the first element and update our result. Return that result. We could also do a right to left BFS and just return the last value.
*/

var findBottomLeftValue = function (root) {
  const deque = [root];
  let leftmostValue;

  while (deque.length > 0) {
    const length = deque.length;
    for (let i = 0; i < length; i++) {
      const node = deque.shift(); // pretend O(1)
      // if it is the first node in a level, grab the value
      if (i === 0) {
        leftmostValue = node.val;
      }

      if (node.left) {
        deque.push(node.left);
      }

      if (node.right) {
        deque.push(node.right);
      }
    }
  }

  return leftmostValue;
};
