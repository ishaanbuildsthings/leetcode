// https://leetcode.com/problems/path-sum-ii/description/
// Difficulty: Medium
// tags: dfs

// Problem
/*
Given the root of a binary tree and an integer targetSum, return all root-to-leaf paths where the sum of the node values in the path equals targetSum. Each path should be returned as a list of the node values, not node references.

A root-to-leaf path is a path starting from the root and ending at any leaf node. A leaf is a node with no children.
*/

// Solution, O(n^2) time and O(n) (height) space. We iterate through n elements, and serialize at up to n leaf nodes.

var pathSum = function (root, targetSum) {
  const result = [];

  function dfs(node, runningNums, currentSum) {
    if (!node) {
      return;
    }

    const newSum = currentSum + node.val;
    runningNums.push(node.val);

    // if we reached the sum and are at a leaf node
    if (newSum === targetSum && !node.left && !node.right) {
      result.push(JSON.parse(JSON.stringify(runningNums)));
    }

    dfs(node.left, runningNums, newSum);
    dfs(node.right, runningNums, newSum);

    runningNums.pop(); // remove the element once we terminate
  }

  dfs(root, [], 0);

  return result;
};
