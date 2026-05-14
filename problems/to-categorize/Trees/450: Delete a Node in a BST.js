// https://leetcode.com/problems/delete-node-in-a-bst/description/
// Difficulty: Medium
// Tags: bst, single branch (recursive or iterative)

// Problem

/*
Given a root node reference of a BST and a key, delete the node with the given key in the BST. Return the root node reference (possibly updated) of the BST.

Basically, the deletion can be divided into two stages:

Search for a node to remove.
If the node is found, delete the node.
*/

// Solution 1, ovewriting values. O(n) (height) time and O(n) (height) space for the callstack.
/*
There are three cases when we remove a node. If the node has no children, we can just chop it off. If it has one child, we would just continue over the node to it's child. And if it has two children, it is a bit more complex. We will write a function that takes in a node, a value, and returns a reference to that root node after the value is removed (if it exists). This is what our desired output is overall, anyways.

We search for the node to remove. Here, I did it recursively reusing the deleteNode function, so that if we hit the node we need to delete, we will wire in the appropriately adjusted subtree. Once we find the node to remove, we return a new subtree. The easy cases return a child, whereas in the complicated case with two children, we need more. We first find the smallest value in that subtree, overwrite the root with that value, then delete that smallest value again recursively.
*/

// finds the minimum value starting from `root`
function findMinVal(root) {
  let current = root;
  let minVal;
  while (current) {
    minVal = current.val;
    current = current.left;
  }
  return minVal;
}

// returns root after the key is removed
var deleteNode = function (root, key) {
  if (!root) {
    return null;
  }

  if (root.val < key) {
    root.right = deleteNode(root.right, key);
  } else if (root.val > key) {
    root.left = deleteNode(root.left, key);
  }
  // we have the node
  else {
    if (!root.left) {
      return root.right; // in a base case, we are removing a root head by returning the remaining branch
    } else if (!root.right) {
      return root.left;
    }
    // the node has two children
    else {
      const minValueFromRight = findMinVal(root.right);
      root.val = minValueFromRight;
      root.right = deleteNode(root.right, minValueFromRight);
    }
  }

  return root;
};
