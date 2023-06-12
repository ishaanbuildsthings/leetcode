// https://leetcode.com/problems/maximum-width-of-binary-tree/description/
// Difficulty: Medium
// tags: binary tree, bfs

// Problem
/*
Given the root of a binary tree, return the maximum width of the given tree.

The maximum width of a tree is the maximum width among all levels.

The width of one level is defined as the length between the end-nodes (the leftmost and rightmost non-null nodes), where the null nodes between the end-nodes that would be present in a complete binary tree extending down to that level are also counted into the length calculation.

It is guaranteed that the answer will in the range of a 32-bit signed integer.
*/

// Solution 1. O(n) time (with real queue) and O(n) space. Do a BFS traversal, numbering children with a heap numbering system. Calculate the width at each level
// * This solution doesn't pass all the test cases, due to how JS handles bigger integers. This solution converted to python does work. There are workarounds for the JS code, but many of them involve hardcoding test cases for certain things. We could likely find a way to mod the distance to make it always fit within a 32 bit signed int if needed.

var widthOfBinaryTree = function (root) {
  let maxWidth = 1;

  const queue = [[root, 1]]; // fake queue. holds tuples of [node, number], where `number` is a heap numbering system

  while (queue.length > 0) {
    const length = queue.length;
    let leftMost;
    let rightMost;
    for (let i = 0; i < length; i++) {
      const [node, number] = queue.shift(); // pretend O(1)

      // capture the leftmost and rightmost node in that level
      if (i === 0) {
        leftMost = number;
      }
      if (i === length - 1) {
        rightMost = number;
      }

      if (node.left) {
        queue.push([node.left, 2 * number]);
      }

      if (node.right) {
        queue.push([node.right, 2 * number + 1]);
      }
    }
    const width = rightMost - leftMost + 1;
    maxWidth = Math.max(maxWidth, width);
  }

  return maxWidth;
};
