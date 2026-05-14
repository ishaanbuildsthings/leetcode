// https://leetcode.com/problems/all-nodes-distance-k-in-binary-tree/description/
// Difficulty: Medium
// Tags: binary tree, graph, recursion

// Problem
/*
Given the root of a binary tree, the value of a target node target, and an integer k, return an array of the values of all nodes that have a distance k from the target node.

You can return the answer in any order.
*/

// Solution, O(n) time and O(n) space
/*
Imagine if this were an acylic graph, it would be very easy to solve, as we just recurse out from the node. So we can assign parent pointers and do that. Instead of actually adding parent pointers in, mutating the structure, we can just populate a hash map.
*/

/**
 * Definition for a binary tree node.
 * function TreeNode(val) {
 *     this.val = val;
 *     this.left = this.right = null;
 * }
 */
/**
 * @param {TreeNode} root
 * @param {TreeNode} target
 * @param {number} k
 * @return {number[]}
 */
var distanceK = function (root, target, k) {
  const parents = new Map(); // maps a node to its parent

  function getParents(node) {
    if (!node) {
      return;
    }

    if (node.left) {
      parents.set(node.left, node);
    }

    if (node.right) {
      parents.set(node.right, node);
    }

    getParents(node.left);
    getParents(node.right);
  }

  getParents(root);

  const seen = new Set(); // tracks seen nodes so we don't recurse multiple times, for instance if we recurse to a parent, that parent shouldn't recurse back to the original neighbor, though this could be avoided by passing in the node we called from

  const result = [];

  function traverse(node, currentDistance) {
    if (!node) {
      return;
    }

    seen.add(node);

    if (currentDistance === k) {
      result.push(node.val);
      return;
    }

    // call parents
    if (parents.has(node)) {
      if (!seen.has(parents.get(node))) {
        traverse(parents.get(node), currentDistance + 1);
      }
    }

    // call children
    if (node.left && !seen.has(node.left)) {
      traverse(node.left, currentDistance + 1);
    }
    if (node.right && !seen.has(node.right)) {
      traverse(node.right, currentDistance + 1);
    }
  }

  traverse(target, 0);

  return result;
};
