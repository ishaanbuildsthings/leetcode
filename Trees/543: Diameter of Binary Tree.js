// https://leetcode.com/problems/diameter-of-binary-tree/description/
// Difficulty: Easy
// tags: binary tree, recursion, top down recursion, bottom up recursion

// Solution 1, bottom up recursion, O(n) time and O(n) memory
/*
Have a dfs function return the max depth it can reach. Start at the bottom, bubbling up the max depths. For any node, see the max depths of its children, and update the diameter if needed. Then, return a max depth based on its children.
*/

var diameterOfBinaryTree = function (root) {
  let maxDiameter = -Infinity;

  // returns the max depth of a node, we update the diameter using it
  function dfs(node) {
    if (!node) return 0;

    const leftNodes = dfs(node.left);
    const rightNodes = dfs(node.right);
    const diameter = leftNodes + rightNodes;
    maxDiameter = Math.max(maxDiameter, diameter);

    return Math.max(1 + leftNodes, 1 + rightNodes);
  }

  dfs(root);

  return maxDiameter;
};

// Solution 2, memoization. O(n) time and O(n) space
/*
Similar to solution 3, but for every subtree, instead of recomputing the max depth, we use a cached value. It takes n time to compute the max depth for each node, and then we iterate through n elements, for each one finding the diameter.
We have to do
*/

var diameterOfBinaryTree = function (root) {
  const cache = new Map(); // maps nodes to their max depths, depth is defined as the number of nodes / levels
  cache.set(null, 0); // to handle edge cases, when a node has null as a child
  function dfsMap(node) {
    if (!node) return 0;

    const leftDepth = dfsMap(node.left);
    const rightDepth = dfsMap(node.right);

    const result = Math.max(1 + leftDepth, 1 + rightDepth);

    cache.set(node, result);
    return result;
  }
  dfsMap(root);
  /* now the cache is populated */

  let maxDiameter = -Infinity;
  // dfs-es through the tree, for each node it checks the diameter by checking its left childs max depth and its right
  function dfsSolve(node) {
    if (!node) return;

    const maxDepthLeft = cache.get(node.left);
    const maxDepthRight = cache.get(node.right);
    const diameter = maxDepthLeft + maxDepthRight; // diamater is really just the number of nodes on the left and right
    maxDiameter = Math.max(maxDiameter, diameter);

    dfsSolve(node.left);
    dfsSolve(node.right);
  }

  dfsSolve(root);

  return maxDiameter;
};

// Solution 3, O(n^2) time and O(n) space, top down with no memoization
/*
For every node, compute the deepest depth of the left and right children, update the max diameter. Worst case is a stick graph where we do n + n-1 + ... 0, which is n^2 time and n space for the stack trace. Best case is in a balanced tree where we have log n layers, and each layer ends up doing n checks as the number of leaves are n (lower bound).
*/

var diameterOfBinaryTree = function (root) {
  let maxDiameter = -Infinity;

  // a normal dfs
  function recurse(node) {
    if (!node) return; // can't DFS if null

    const diameter = maxDepth(node.left) + maxDepth(node.right);
    maxDiameter = Math.max(maxDiameter, diameter);

    recurse(node.left);
    recurse(node.right);
  }

  recurse(root);

  return maxDiameter;
};

// computes how deep we can go from a given node
function maxDepth(node) {
  if (!node) return 0;
  return Math.max(1 + maxDepth(node.left), 1 + maxDepth(node.right));
}
