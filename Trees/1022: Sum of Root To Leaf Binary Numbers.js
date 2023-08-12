//  https://leetcode.com/problems/sum-of-root-to-leaf-binary-numbers/description/
// difficulty: easy
// tags: binary tree

// Problem
/*
You are given the root of a binary tree where each node has a value 0 or 1. Each root-to-leaf path represents a binary number starting with the most significant bit.

For example, if the path is 0 -> 1 -> 1 -> 0 -> 1, then this could represent 01101 in binary, which is 13.
For all leaves in the tree, consider the numbers represented by the path from the root to that leaf. Return the sum of these numbers.

The test cases are generated so that the answer fits in a 32-bits integer.
*/

// Solution, O(n) time, O(height) space
/*
Just DFS and maintain a bit number, when we get to a leaf add it to the sum.
*/

var sumRootToLeaf = function (root) {
  let sum = 0;

  function dfs(node, bits) {
    if (node.val === 1) {
      bits = (bits << 1) | 1;
    } else {
      bits = bits << 1;
    }

    // if we are at a leaf node, add the number
    if (!node.left && !node.right) {
      sum += bits;
    }

    if (node.left) {
      dfs(node.left, bits);
    }

    if (node.right) {
      dfs(node.right, bits);
    }
  }

  dfs(root, 0);

  return sum;
};
