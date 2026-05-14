// https://leetcode.com/problems/recover-binary-search-tree/description/
// tags: inorder, arrays, bst

// Problem
/*
You are given the root of a binary search tree (BST), where the values of exactly two nodes of the tree were swapped by mistake. Recover the tree without changing its structure.
*/

// Solution, O(n) time and O(n) (height) space.
/*
Do an inorder traversal, which for BSTs should be ascending. Maintain the highest previous value we have seen. When we process the current node, see if it violates the rule. If so, update the bad nodes. The bad nodes are based on the principle of an almost sorted array, which is a sorted array with two swapped elements. This can be fixed using the technique outlined in the explanations file under tricky array techiques, for problem 99.
*/

var recoverTree = function (root) {
  let prevHighest = -Infinity;
  let prevNode = null;
  const badNodes = [];
  // do an inorder dfs
  function dfs(node) {
    if (!node) {
      return;
    }

    dfs(node.left);

    if (node.val < prevHighest) {
      if (badNodes.length === 0) {
        badNodes.push(prevNode);
        badNodes.push(node);
      } else if (badNodes.length === 2) {
        badNodes[1] = node;
      }
    }
    prevHighest = node.val;
    prevNode = node;

    dfs(node.right);
  }

  dfs(root);

  const temp = badNodes[0].val;
  badNodes[0].val = badNodes[1].val;
  badNodes[1].val = temp;

  return root;
};
