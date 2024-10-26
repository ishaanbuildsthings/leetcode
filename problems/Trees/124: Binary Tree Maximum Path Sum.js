// https://leetcode.com/problems/binary-tree-maximum-path-sum/description/
// Difficulty: Hard
// tags: binary tree, dfs

// Solution, O(n) time and O(n) (height) space for the callstack.

/*
For a given node, we should know the best left descendants we can keep, and the best right descendants. If the descendants sum is negative, we would just set it to 0, kind of like in kadane's. We then check our sum assuming that node is a root and we pass from the left to right of it, updating max sum if needed. We then bubble up the optimal single path to the higher nodes.
*/

var maxPathSum = function (root) {
  let maxSum = -Infinity;

  /*
    we are basically computing sum paths starting from the bottom up. If our sum path is negative, reset it to 0. For a given node, if we assume that node is the root and it passes from the left of that node to the right, our max sum is the biggest left sum path + the biggest right sum path + the node itself.
    */
  function dfs(node) {
    // if we have null, the max sum we can make with that node as a root and our path going from the left to right of it, is 0
    if (!node) {
      return 0;
    }

    const leftPathSum = dfs(node.left);
    const rightPathSum = dfs(node.right);
    const sum = leftPathSum + rightPathSum + node.val;

    maxSum = Math.max(maxSum, sum);

    let maxSinglePath = Math.max(
      leftPathSum + node.val,
      rightPathSum + node.val
    );
    if (maxSinglePath < 0) {
      maxSinglePath = 0;
    }

    return maxSinglePath;
  }

  dfs(root);

  return maxSum;
};
