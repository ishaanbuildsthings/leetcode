// https://leetcode.com/problems/balanced-binary-tree/description/
// Difficulty: Easy
// tags: binary tree, top down recursion, dfs, bottom up recursion

// Solution 1, bottom up recursion, dfs
// Time: O(n), space O(n)
/*
To know if a given is balanced, we must know that all of the subtrees are balanced. We then also need to compare the heights of the left and right subtrees to determine if that node is balanced. It is possible the heights can be the same, but the root still is not balanced, because maybe one of the subtrees somewhere is not balanced, for instance:
      O
     / \
    O   O
   /     \
  O       O
 /         \
O           O

 Here, the left and right branches have the same height, but the root still is not balanced because there are unbalanced subtrees.

 If we started from the top, we would calculate the max depth of the left and right, and compare them. If that checks out, we recurse down further. The problem is that as we recurse down, we do a lot of repeated work as we re-calculate max depths for things. For instance to calculate the max depth of the root, we calculate the max depth for the left and right child. But then when we need to calculate the max depth for one of those nodes, we recalculate it. We can avoid this with bottom up recursion. We first dfs down to the bottom (as long as we are not null). Then when we reach null, we return both that we are balanced and our height. This allows us to process and re-use data regarding the depth of things. Now for a non-null node we compare the two heights. If they are within range, that is good. But if any of those children are not balanced, the main node is not balanced, so we bubble that up.

 The algorithm can be improved a bit in practice, since as soon as we see a non-balanced tree we can return false. For instance in between getting the leftBalanced and rightBalanced values, we can check if leftBalanced is true. If it is not, we just return [false] (in an array since at the end of the function we return dfs(root)[0]).

 We could probably do a top down recursive call where we cache a mapping of nodes to their heights, so we can reuse that. And then delete the mappings when they are no longer needed, so the overall memory usage stays comparable to the bottom up (in average, balanced scenarios).

 Bottom up is more like tabulation, where we start from simple cases and fill things up based on the earlier results. It requires a forced order. Whereas top down / memoization kind of assumes we have an answer already. One benefit of top down is we might be able to more sparsley fill out our cache, whereas tabulation might need all values filled. For instance if we have a pattern where a number is the sum of the number 5 indices before it, and we start with: 0 1 2 3 4, and we need to calculate the 10th number. In memoization, we might check the 5th number and see it is a 4. But in tabulation, we might fill out the table one by one until we reach the 10th number. Memoization might need extra stack frame memory (think fibonacci) whereas tabulation could potentially be done without stack fames (populating a DP array starting from the beginning), so there are tradeoffs.
*/
var isBalanced = function (root) {
  return dfs(root)[0];
};

// takes in a node, returns a boolean if it is balanced, and the height of the tree
function dfs(node) {
  if (!node) return [true, 0]; // null nodes are balanced and have no height

  const [leftBalanced, leftHeight] = dfs(node.left);
  const [rightBalanced, rightHeight] = dfs(node.right);

  const heightDifference = Math.abs(leftHeight - rightHeight);
  if (heightDifference > 1 || !leftBalanced || !rightBalanced) {
    return [false, Math.max(leftHeight, rightHeight) + 1];
  }

  return [true, Math.max(leftHeight, rightHeight) + 1];
}

// Solution 2, top down recursion (no memoization)
// Time: O(n^2), space O(n)
/*
For every node, run a max depth on its left and right children, and compare them. For any given node, we basically analyze all the nodes underneath it to determine the max depth. Worst case is a stick graph where we do n+ n-1 + n-2 ... + 0, which is n^2. Best case is a balanced tree which has depth of log n, and each layer has n checks (as all leaves are n, lower bound). The memory at any point is the max depth of the tree due to the call stack.
*/

var isBalanced = function (node) {
  if (!node) return true; // if the node is null, it is height balanced

  // if we have a node, see how far down we can go left and right, and check the differences
  const leftDepth = maxDepth(node.left);
  const rightDepth = maxDepth(node.right);
  if (Math.abs(leftDepth - rightDepth) > 1) {
    return false;
  }

  // if from that node, the left and right are balanced, repeat the checking process on both children

  return isBalanced(node.left) && isBalanced(node.right);
};

// finds the depth of a tree
function maxDepth(node) {
  if (!node) return 0;
  else {
    return Math.max(1 + maxDepth(node.left), 1 + maxDepth(node.right));
  }
}

// Solution 3, top down recursion (with memoization)
// Time O(n), space O(n)
/*
We make a cache for our helper function, max depth, that maps a node to its max depth. Now, as we traverse through the tree, doing maxdepth calls on a node's left and right child, they will be cached, as a result of the initial call to root.
*/

var isBalanced = function (node) {
  const cache = new Map();
  // finds the depth of a tree
  function maxDepth(node) {
    if (!node) return 0;
    if (cache.has(node)) {
      return cache.get(node);
    }

    const result = Math.max(1 + maxDepth(node.left), 1 + maxDepth(node.right));
    cache.set(node, result);
    return result;
  }

  if (!node) return true; // if the node is null, it is height balanced

  // if we have a node, see how far down we can go left and right, and check the differences
  const leftDepth = maxDepth(node.left);
  const rightDepth = maxDepth(node.right);
  if (Math.abs(leftDepth - rightDepth) > 1) {
    return false;
  }

  // if from that node, the left and right are balanced, repeat the checking process on both children

  return isBalanced(node.left) && isBalanced(node.right);
};
