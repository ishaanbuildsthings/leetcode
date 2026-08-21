// https://leetcode.com/problems/lowest-common-ancestor-of-a-binary-tree-ii/description/
// Difficulty: Medium
// Tags: binary tree, bottom up recursion, lca

// Problem
/*
Given the root of a binary tree, return the lowest common ancestor (LCA) of two given nodes, p and q. If either node p or q does not exist in the tree, return null. All values of the nodes in the tree are unique.

According to the definition of LCA on Wikipedia: "The lowest common ancestor of two nodes p and q in a binary tree T is the lowest node that has both p and q as descendants (where we allow a node to be a descendant of itself)". A descendant of a node x is a node y that is on the path from node x to some leaf node.
*/

// Solution, O(n) time and O(n) (height) space
/*
Recurse down to the bottom first. In general, check which values have been seen from the left or right subtrees. Bubble up accordingly. If a tree has both of its children containing p and q, we just bubble up that lowest common ancestor instead. I had separate variables for p and q but you can actually just maintain a count of how many of p and q have been seen. Also if we used an iterative stack we could terminate early when the result is found.
*/

var lowestCommonAncestor = function (root, p, q) {
  if (!p || !q) return null; // weird edge case / maybe bug from leetcode

  function postorder(node) {
    if (!node) {
      return [false, false];
    }

    const leftResult = postorder(node.left);
    const rightResult = postorder(node.right);

    if (!Array.isArray(leftResult)) {
      return leftResult;
    }

    if (!Array.isArray(rightResult)) {
      return rightResult;
    }

    const [leftHasP, leftHasQ] = leftResult;
    const [rightHasP, rightHasQ] = rightResult;

    // if we aren't one of the nodes, either check if both subtrees combine to have the nodes, or just forward which ones do
    if (node.val !== p.val && node.val !== q.val) {
      if ((leftHasP && rightHasQ) || (leftHasQ && rightHasP)) {
        return node;
      }
      return [leftHasP || rightHasP, leftHasQ || rightHasQ];
    } else if (node.val === p.val) {
      if (leftHasQ || rightHasQ) {
        return node;
      } else {
        return [true, false]; // we have p but not q
      }
    } else if (node.val === q.val) {
      if (leftHasP || rightHasP) {
        return node;
      } else {
        return [false, true];
      }
    }
  }

  return postorder(root);
};
