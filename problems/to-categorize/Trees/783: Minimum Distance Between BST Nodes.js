// https://leetcode.com/problems/minimum-distance-between-bst-nodes/description/
// Difficulty: Easy
// tags: trees, bst, inorder

// Problem
/*
Given the root of a Binary Search Tree (BST), return the minimum difference between the values of any two different nodes in the tree.
*/

/*
Solution 1, O(n) time and O(h) space. Do an inorder recursive traversal, and keep track of the previous node. Compare the current node to the previous node, and update the minDifference if necessary.
The intuition for this is:

Initially, prevNode is null. This makes sense, because at the very first node, we have nothing to compare it to. We also use the concept of a previous node, rather than a future node, because we can't know what value the future node has (that would be more complicated and maybe require extra backtracking).

So we recurse down to the bottom left node. When we hit null, we pop back up and return. At the bottom left node, we assign prev to that node, this is our first node! We also check the difference between the previous node and the current one, but this happens before, and only if prevNode wasn't null, as we don't check for the very first case.
*/

var minDiffInBST = function (root) {
  let minDifference = Infinity;
  let prevNode = null;

  function inorder(node) {
    if (!node) {
      return;
    }

    inorder(node.left);

    if (prevNode !== null) {
      const currentDifference = node.val - prevNode.val;
      minDifference = Math.min(minDifference, currentDifference);
    }

    prevNode = node;

    inorder(node.right);

    return node;
  }

  inorder(root);

  return minDifference;
};

// Solution 2, same thing as solution 1, inorder traversal, but we use a list, so O(n) space

var minDiffInBST = function (root) {
  const order = [];
  function inorder(node) {
    if (!node) {
      return;
    }
    inorder(node.left);
    order.push(node.val);
    inorder(node.right);
  }

  inorder(root);

  let min = Infinity;
  for (let i = 0; i < order.length - 1; i++) {
    min = Math.min(min, Math.abs(order[i] - order[i + 1]));
  }

  return min;
};
