// https://leetcode.com/problems/invert-binary-tree/description/
// Difficulty: Easy

// Problem
/*
Given the root of a binary tree, invert the tree, and return its root.
*/

// Solution, O(n) time and O(n) space, where n is the number of nodes in the tree, since we need to invert every node, and n (for space) is the depth of the tree, where worst case n=number of nodes. Create a recursive function that inverts the two children, then calls those two children.

var invertTree = function (root) {
  function invertChildren(node) {
    if (!node) {
      return;
    }
    const temp = node.left;
    node.left = node.right;
    node.right = temp;
    invertChildren(node.left);
    invertChildren(node.right);
  }
  invertChildren(root);
  return root;
};
