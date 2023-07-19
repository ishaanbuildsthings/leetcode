// https://leetcode.com/problems/maximum-sum-bst-in-binary-tree/description/
// Difficulty: Hard
// Tags: binary tree, recursion, bottom up recursion

// Problem
/*
Given a binary tree root, return the maximum sum of all keys of any sub-tree which is also a Binary Search Tree (BST).

Assume a BST is defined as follows:

The left subtree of a node contains only nodes with keys less than the node's key.
The right subtree of a node contains only nodes with keys greater than the node's key.
Both the left and right subtrees must also be binary search trees.
*/

// Solution, O(n) time, O(n) (height) space
/*
First, we have to make some observations.

Not every binary tree is a BST, so we want to know when we have a BST or not. We could solve this brute force, where we check every tree from every node, but it would likely TLE due to n^2, so I thought I could bubble up nformation from the bottom nodes.

To know if I have a bst, I have to know if my left and right children are bsts, and my root node lands in a certain range. It must be bigger than the largest value from the left subtree, and smaller than the biggest value in the right subtree. Because of this, we track the largest and smallest values seen as we bubble up. Importantly, we cannot just compare a node to its direct children.

If we are not a BST, no ancestor node that includes us can be a bst. So we can just bubble up the biggest bst we have ever seen.

If we are a bst, we can bubble up both the current max sum of our bst where the current node is the root, as well as the biggest bst ever seen. This comes into play with negatives, for instance:

    50
  -10
    5

    Clearly, the max bst sum is 45, so we need to include a negative tree.

    But:
     10
  -100
     8
      9

    Here, the -10 is a valid bst, but we also need to send up a 17, the max bst sum we have ever seen.

  Anyway, I got stuck on a few test cases until I added extra parameters to track all this information. It was a process of failing test cases that illuminated things wrong in my initial solution. I don't think the above examples fully prove anything, but I am sure there is a way to construct an exhaustive proof that bubbling up both pieces of information is required, and always works.
*/

var maxSumBST = function (root) {
  /*
    dfs returns [isBst,
                 max bst sum so far,
                 current bst sum (includes root for sure) and is null if not a bst,
                 smallest element seen,
                 largest element seen
                 ]
    */
  function dfs(node) {
    // base case, a null node is a bst with a sum of 0
    if (!node) {
      return [true, 0, 0, Infinity, -Infinity];
    }

    const [
      isLeftBst,
      leftMaxBstSum,
      leftCurrentBstSum,
      smallestLeft,
      largestLeft,
    ] = dfs(node.left);
    const [
      isRightBst,
      rightMaxBstSum,
      rightCurrentBstSum,
      smallestRight,
      largestRight,
    ] = dfs(node.right);

    const biggestValueSoFar = Math.max(node.val, largestLeft, largestRight);
    const smallestValueSoFar = Math.min(node.val, smallestLeft, smallestRight);

    // we are a bst if we are the larger than the largest from the left bst, smaller than the smallest from the right bst, and the left and right children are bsts

    // if we cannot form a bst based on the two children, or one of the children isn't a bst, we cannot be a bst
    if (
      node.val <= largestLeft ||
      node.val >= smallestRight ||
      !isLeftBst ||
      !isRightBst
    ) {
      return [
        false,
        Math.max(leftMaxBstSum, rightMaxBstSum),
        null,
        smallestValueSoFar,
        biggestValueSoFar,
      ];
    }

    /* here, we can form a bst */
    const bstSumIfUsingRoot = node.val + leftCurrentBstSum + rightCurrentBstSum;
    const maxBstFromChildren = Math.max(leftMaxBstSum, rightMaxBstSum);
    const biggestBst = Math.max(bstSumIfUsingRoot, maxBstFromChildren);
    return [
      true,
      biggestBst,
      bstSumIfUsingRoot,
      smallestValueSoFar,
      biggestValueSoFar,
    ];
  }

  const result = dfs(root)[1];
  // this happens when all the nodes are negative
  if (result < 0) {
    return 0;
  }
  return result;
};
