// https://leetcode.com/problems/univalued-binary-tree/description/
// Difficulty: Easy
// Tags: binary tree

// Problem
/*
A binary tree is uni-valued if every node in the tree has the same value.

Given the root of a binary tree, return true if the given tree is uni-valued, or false otherwise.
*/

// Solution, O(n) time and O(n) (height) space. Just compare a value with its children and recurse.

var isUnivalTree = function (root) {
  if (!root) {
    return true;
  }

  if (root.left && root.left.val !== root.val) {
    return false;
  }

  if (root.right && root.right.val !== root.val) {
    return false;
  }

  return isUnivalTree(root.left) && isUnivalTree(root.right);
};
