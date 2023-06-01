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

 We could probably do a top down recursive call where we cache a mapping of nodes to their heights, so we can reuse that. One problem might be a naive implementation would cache every node in memory, which would perform worse than the bottom up recursive code, for more balanced trees. Because on a more balanced tree, the recursive code approaches log n storage (depth of callstack) whereas the cache might have all the nodes still. Worst case they are both n though.
*/
var isBalanced = function (root) {
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

  return dfs(root)[0];
};

// Solution 2, top down recursion
// Time: O(n^2), space O(n)
/*
For every node, run a max depth on its left and right children, and compare them. For any given node, we basically analyze all the nodes underneath it to determine the max depth. Since in a balanced tree the leaves are still n, we might be doing n checks for n nodes, resulting in n^2 time. The memory at any point is the max depth of the tree due to the call stack.
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
