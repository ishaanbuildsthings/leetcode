// https://leetcode.com/problems/lowest-common-ancestor-of-a-binary-search-tree/description/
// Difficulty: Medium
// tags: bst, single branch (recursive or iterative)

// Problem
/*
Given a binary search tree (BST), find the lowest common ancestor (LCA) node of two given nodes in the BST.

According to the definition of LCA on Wikipedia: “The lowest common ancestor is defined between two nodes p and q as the lowest node in T that has both p and q as descendants (where we allow a node to be a descendant of itself).”
*/

// Solution 1, iterative, O(n) time and O(1) space
/*
Keep iterating, when we diverge or find one of the nodes, we can return the current node.
*/

var lowestCommonAncestor = function (root, p, q) {
  let current = root;
  while (true) {
    // both are on the right
    if (current.val < p.val && current.val < q.val) {
      current = current.right;
    }
    // both are left
    else if (current.val > p.val && current.val > q.val) {
      current = current.left;
    }
    // one is left, the other is right, we found the LCA
    else if (
      (current.val > p.val && current.val < q.val) ||
      (current.val < p.val && current.val > q.val)
    ) {
      return current;
    }
    // we found one of the nodes
    else if (current.val === p.val || current.val === q.val) {
      return current;
    }
  }
};

// Solution 2, single branch recursion, O(n) time and O(n) space
/*
The recursive function checks if we have found the value or if we diverged. Otherwise we recurse on either the left or right.
*/

var lowestCommonAncestor = function (root, p, q) {
  if (root.val === p.val || root.val === q.val) {
    return root;
  } else if (root.val < p.val && root.val < q.val) {
    return lowestCommonAncestor(root.right, p, q);
  } else if (root.val > p.val && root.val > q.val) {
    return lowestCommonAncestor(root.left, p, q);
  }
  // we have to diverge
  else {
    return root;
  }
};
