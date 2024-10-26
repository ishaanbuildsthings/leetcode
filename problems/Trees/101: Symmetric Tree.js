// https://leetcode.com/problems/symmetric-tree/description/
// Difficulty: Easy
// tags: dfs

// Problem
// Given the root of a binary tree, check whether it is a mirror of itself (i.e., symmetric around its center).

// Solution, O(n) time and O(n) (height) space.
/*
Create a dual dfs function which dfs's across two trees at the same time. We run this dual dfs on root.left and root.right. It compares the values, and if they match, runs a dual dfs on the mirrored children.
*/

var isSymmetric = function (root) {
  function dualDfs(node1, node2) {
    // if both trees are null, they are the same
    if (!node1 && !node2) {
      return true;
    }

    // if only one is null, they are different
    if (!node1 || !node2) {
      return false;
    }

    // if they are nodes but have different values, they are different
    if (node1.val !== node2.val) {
      return false;
    }

    return dualDfs(node1.left, node2.right) && dualDfs(node1.right, node2.left);
  }

  if (!root) return true;

  return dualDfs(root.left, root.right);
};
