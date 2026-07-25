// https://leetcode.com/problems/search-in-a-binary-search-tree/description/
// Difficulty: Easy
// tags: bst

// Solution 1, iterative, O(log n) time (balanced BST) and O(1) space
/*
Start at the root, and move accordingly based on the comparison of that nodes value and the target value.
*/
var searchBST = function (root, val) {
  let node = root;
  while (node) {
    if (node.val < val) {
      node = node.right;
    } else if (node.val === val) {
      return node;
    } else if (node.val > val) {
      node = node.left;
    }
  }
  return null;
};

// Solution 2, recursive, O(log n) time and O(log n) space (both assuming balanced BST)
/*
If we are null, return null. Otherwise, if we are less than the target, recurse right. If we are greater than the target, recurse left. If we are equal to the target, return the node. It might be more intuitive if we check if we are equal before we search left or right.
*/
var searchBST = function (node, val) {
  if (!node) return null;

  if (node.val < val) {
    return searchBST(node.right, val);
  } else if (node.val > val) {
    return searchBST(node.left, val);
  } else if (node.val === val) {
    return node;
  }
};
