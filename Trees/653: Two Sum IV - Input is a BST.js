// https://leetcode.com/problems/two-sum-iv-input-is-a-bst/description/
// Difficulty: Easy

// Problem
/*
Given the root of a binary search tree and an integer k, return true if there exist two elements in the BST such that their sum is equal to k, or false otherwise.
*/

// Solution, O(n) time and O(n) space
// * You could also have two BST iterators (which run in O(height) space). Since it is a BST, inorder runs in order. We then basically use a 2-pointer solution to find the two sum.
/*
I added all numbers to a set, then checked, for each number in the set, if the complement was in the set.
*/

var findTarget = function (root, k) {
  const numSet = new Set();

  function dfs(node) {
    if (!node) {
      return;
    }
    numSet.add(node.val);
    dfs(node.left);
    dfs(node.right);
  }

  dfs(root);

  for (const num of Array.from(numSet)) {
    if (numSet.has(k - num) && k !== 2 * num) {
      // no duplicate values in BSTs, so we can't reuse a number twice
      return true;
    }
  }

  return false;
};
