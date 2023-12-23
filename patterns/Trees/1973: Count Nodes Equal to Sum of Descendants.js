// https://leetcode.com/problems/count-nodes-equal-to-sum-of-descendants/description/
// difficulty: Medium
// tags: binary tree

// Problem
/*
Given the root of a binary tree, return the number of nodes where the value of the node is equal to the sum of the values of its descendants.

A descendant of a node x is any node that is on the path from node x to some leaf node. The sum is considered to be 0 if the node has no descendants.
 */

// Solution, O(n) time and O(n) (height) space
/*
DFS down, and bubble up sums. If the sums of the children equal the current node, add one to the result.
*/

var equalToDescendants = function (root) {
  let result = 0;

  function dfs(node) {
    if (!node) {
      return 0;
    }

    const leftSum = dfs(node.left);
    const rightSum = dfs(node.right);

    if (node.val === leftSum + rightSum) {
      result++;
    }

    return leftSum + rightSum + node.val;
  }

  dfs(root);

  return result;
};
