// https://leetcode.com/problems/insert-into-a-binary-search-tree/description/
// Difficulty: Medium
// tags: bst

// Problem
/*
You are given the root node of a binary search tree (BST) and a value to insert into the tree. Return the root node of the BST after the insertion. It is guaranteed that the new value does not exist in the original BST.

Notice that there may exist multiple valid ways for the insertion, as long as the tree remains a BST after insertion. You can return any of them.
*/

// Solution, O(log n) time, assuming a balanced tree, and O(1) space.
/*
Since we can insert the node anywhere, just keep descending until we find the insertion point. Also handle the initial edge case if our root is null.
*/

var insertIntoBST = function (root, val) {
  if (!root) {
    return new TreeNode(val);
  }

  let node = root;
  while (node) {
    // we need to insert right
    if (node.val < val) {
      if (!node.right) {
        node.right = new TreeNode(val);
        return root;
      }
      node = node.right;
    }
    // we need to insert left
    else {
      if (!node.left) {
        node.left = new TreeNode(val);
        return root;
      }
      node = node.left;
    }
  }
};
