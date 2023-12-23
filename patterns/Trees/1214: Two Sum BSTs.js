// https://leetcode.com/problems/two-sum-bsts/description/
// Difficulty: Medium
// tags: binary tree, inorder, two pointers

// Problem
/*
Given the roots of two binary search trees, root1 and root2, return true if and only if there is a node in the first tree and a node in the second tree whose values sum up to a given integer target.
*/

// Solution, O(n) time and O(n) space
// * Solution 2, do an inorder traversal of both trees. Say: [1, 3, 9, 12] and [5, 11, 14, 16]. Put one pointer on the left of one array, and another on the right of the second array. If the sum is too big, decrement the right pointer, otherwise increment the left. This is similar to the 2sum sorted array problem. It still works, because logically, if the required sum is smaller than what we have, we must decrement, otherwise we must increment.

/*
Do a traversal of both trees, storing the numbers in the trees in separate sets. Iterate through the first set, check if the required number is in the second set.
*/

var twoSumBSTs = function (root1, root2, target) {
  const tree1Set = new Set();
  const tree2Set = new Set();

  function dfs(node, treeSet) {
    if (!node) {
      return;
    }

    dfs(node.left, treeSet);
    dfs(node.right, treeSet);
    treeSet.add(node.val);
  }

  dfs(root1, tree1Set);
  dfs(root2, tree2Set);

  for (const value of Array.from(tree1Set)) {
    const secondNumNeeded = target - value;
    if (tree2Set.has(secondNumNeeded)) {
      return true;
    }
  }

  for (const value of Array.from(tree2Set)) {
    const secondNumNeeded = target - value;
    if (tree1Set.has(secondNumNeeded)) {
      return true;
    }
  }

  return false;
};
