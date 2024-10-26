// https://leetcode.com/problems/trim-a-binary-search-tree/description/
// Difficulty: Medium
// tags: bst

// Problem
/*
Given the root of a binary search tree and the lowest and highest boundaries as low and high, trim the tree so that all its elements lies in [low, high]. Trimming the tree should not change the relative structure of the elements that will remain in the tree (i.e., any node's descendant should remain a descendant). It can be proven that there is a unique answer.

Return the root of the trimmed binary search tree. Note that the root may change depending on the given bounds.
*/

// Solution 1, O(n) time and O(n) space where the space is the height of the callstack.

/*
The overall goal of trimBST is to take in a root, and return the trimmed version of it, so we can use this recursively. We have a few cases:

1) The root is null, there is nothing to trim, so we return null.

2) The root is too big, meaning anything to the right is also too big. We can return the trimming of the left subtree.

3) The root is too small, meaning anything to the left is also too small. We can return the trimming of the right subtree.

If the root is in range, we need to trim the left and right, and return the root.
*/

var trimBST = function (root, low, high) {
  // base case, we have nothing to trim
  if (!root) {
    return null;
  }

  if (root.val > high) {
    return trimBST(root.left, low, high);
  }

  if (root.val < low) {
    return trimBST(root.right, low, high);
  }

  root.right = trimBST(root.right, low, high);
  root.left = trimBST(root.left, low, high);

  return root;
};
