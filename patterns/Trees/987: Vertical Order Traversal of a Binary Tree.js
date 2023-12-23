// https://leetcode.com/problems/vertical-order-traversal-of-a-binary-tree/description/
// Difficulty: Hard
// Tags: Trees

// Problem
/*
Given the root of a binary tree, calculate the vertical order traversal of the binary tree.

For each node at position (row, col), its left and right children will be at positions (row + 1, col - 1) and (row + 1, col + 1) respectively. The root of the tree is at (0, 0).

The vertical order traversal of a binary tree is a list of top-to-bottom orderings for each column index starting from the leftmost column and ending on the rightmost column. There may be multiple nodes in the same row and same column. In such a case, sort these nodes by their values.

Return the vertical order traversal of the binary tree.
*/

// Solution, O(n log n) time, O(height + sort) space
/*
First, iterate through the nodes, storing tuples with their rows and columns. This takes n time and height space. Then, sort the tuples which takes n time and sort space. Then, for each tuple, create appropriate buckets.
*/

/**
 * Definition for a binary tree node.
 * function TreeNode(val, left, right) {
 *     this.val = (val===undefined ? 0 : val)
 *     this.left = (left===undefined ? null : left)
 *     this.right = (right===undefined ? null : right)
 * }
 */
/**
 * @param {TreeNode} root
 * @return {number[][]}
 */
var verticalTraversal = function (root) {
  const nodes = []; // stores tuples of [node, row, col]

  function dfs(node, row, col) {
    nodes.push([node, row, col]);
    if (node.left) {
      dfs(node.left, row + 1, col - 1);
    }
    if (node.right) {
      dfs(node.right, row + 1, col + 1);
    }
  }

  dfs(root, 0, 0);

  nodes.sort((a, b) => {
    // first columns go first
    if (a[2] !== b[2]) {
      return a[2] - b[2];
    }
    // if columns are the same, sort by row
    if (a[1] !== b[1]) {
      return a[1] - b[1];
    }
    // otherwise by value
    return a[0].val - b[0].val;
  });

  const result = [];
  let bucket = []; // stores a full column
  let currentCol = nodes[0][2];
  for (let i = 0; i < nodes.length; i++) {
    const tuple = nodes[i];
    const [node, row, col] = tuple;
    if (col !== currentCol) {
      result.push(bucket);
      bucket = [];
      currentCol++;
    }
    bucket.push(node.val);
  }
  result.push(bucket);
  return result;
};
