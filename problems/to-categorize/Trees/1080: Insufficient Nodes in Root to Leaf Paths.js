// https://leetcode.com/problems/insufficient-nodes-in-root-to-leaf-paths/description/
// difficulty: Medium
// tags: binary tree

// Problem
/*
Given the root of a binary tree and an integer limit, delete all insufficient nodes in the tree simultaneously, and return the root of the resulting binary tree.

A node is insufficient if every root to leaf path intersecting this node has a sum strictly less than limit.

A leaf is a node with no children.
*/

// Solution, O(n) time and O(n) (height) space
/*
We are insufficient, if at every subtree, given our current accumulated sum, we have a sum less than limit. What this means is as we descend, we accrue our sum. When we are at a leaf node, that is the base case, and we check if we acrrued enough sum, and return if we should be deleted or not. In general, we check if every path on the left needs to be deleted, and every path on the right. Based on which paths should be deleted, we assign those to null. If both of those paths need to be deleted, then so does our current node.
*/

var sufficientSubset = function (root, limit) {
  const dummy = new TreeNode(0);
  dummy.left = root;

  function dfs(node, currentSum) {
    if (!node) {
      return true; // helps the case when a node just has one child
    }

    // if we are a leaf node, we delete it if the single path that goes through the leaf is below the limit
    if (!node.left && !node.right) {
      if (currentSum + node.val < limit) {
        return true; // delete the node
      }
      return false;
    }

    // if we aren't a leaf node, we should delete the node if every path below us needs to be deleted
    const everyLeftPathNeedsToBeDeleted = dfs(node.left, currentSum + node.val);
    const everyRightPathNeedsToBeDeleted = dfs(
      node.right,
      currentSum + node.val
    );

    if (everyLeftPathNeedsToBeDeleted) {
      node.left = null;
    }
    if (everyRightPathNeedsToBeDeleted) {
      node.right = null;
    }

    if (everyLeftPathNeedsToBeDeleted && everyRightPathNeedsToBeDeleted) {
      return true; // delete the node
    }

    return false;
  }

  dfs(dummy, 0);

  return dummy.left;
};
