// https://leetcode.com/problems/convert-binary-search-tree-to-sorted-doubly-linked-list/description/
// Difficulty: Medium
// Tags: bst, inorder

// Problem
/*
Convert a Binary Search Tree to a sorted Circular Doubly-Linked List in place.

You can think of the left and right pointers as synonymous to the predecessor and successor pointers in a doubly-linked list. For a circular doubly linked list, the predecessor of the first element is the last element, and the successor of the last element is the first element.

We want to do the transformation in place. After the transformation, the left pointer of the tree node should point to its predecessor, and the right pointer should point to its successor. You should return the pointer to the smallest element of the linked list.
*/

// Solution, O(n) time, O(n) (height) space for the callstack

/*
The easiest way to do this is to store all the nodes in a list (in an inorder traversal), then perform the linkages. But since we can't do that due to the in-place requirement, we do the following:

I initially tried to return things from the inorder traversal, but this isn't needed. At any node, we just need access to the previous node, so we can wire those in. Then we call the next node (which is handled via the inorder traversal).

So we maintain a prev global variable. When we process a node, we wire the previous node in with this node. That's it. We have to check if the previous value is valid, or the initialized null value. We also track the smallest and largest values to do some rewiring at the end.
*/

var treeToDoublyList = function (root) {
  // edge case
  if (!root) {
    return null;
  }

  let smallest = new Node(Infinity);
  let largest = new Node(-Infinity);

  let prev = null;

  function inorder(node) {
    if (!node) {
      return;
    }

    if (node.val < smallest.val) {
      smallest = node;
    }

    if (node.val > largest.val) {
      largest = node;
    }

    inorder(node.left);

    if (prev) {
      prev.right = node;
      node.left = prev;
      prev = node;
    } else {
      prev = node;
    }

    inorder(node.right);
  }

  inorder(root);

  smallest.left = largest;
  largest.right = smallest;

  return smallest;
};
