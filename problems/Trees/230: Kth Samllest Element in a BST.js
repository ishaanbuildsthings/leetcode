// https://leetcode.com/problems/kth-smallest-element-in-a-bst/description/
// Difficulty: Medium
// tags: bst, inorder traversal

// Problem
/*
Given the root of a binary search tree, and an integer k, return the kth smallest value (1-indexed) of all the values of the nodes in the tree.
*/

// Solution 1, O(n) time and O(n) space. Really, the time is O(height + k), as worst case we iterate down the height of the tree, then check k elements. The space is also O(height).

/*
Do an inorder traversal. Whenever we 'see' an element (in order), we increment the amount we have seen. If we have seen k elements, return that element up to the top.
*/

var kthSmallest = function (root, k) {
  let inorderElementsSeen = 0;

  // does an inorder traversal
  function inorder(node) {
    if (!node) return null;

    const leftInorder = inorder(node.left);
    if (leftInorder !== null) {
      return leftInorder;
    }

    inorderElementsSeen++;
    if (inorderElementsSeen === k) {
      return node.val;
    }

    const rightInorder = inorder(node.right);
    if (rightInorder !== null) {
      return rightInorder;
    }

    return null; // if we didn't reach the kth element
  }

  return inorder(root);
};

/*
            5
          /   \
         3     6
        / \
       2   4
      /
     1

     we call inorder on 5, calling it on 3
     4) the call on 3 returned a 3, so we return 3

     inorder on 3 calls it on 2
     3) we have now seen 3, we increment the elements, we reached k, so we return the value 3
        the callstack on value 3 now ends

     inorder on 2 calls it on 1
     2) we have now seen 2, we incremenet elements seen
        we call it on 2s right, terminating
        the callstack for 2 ended, we forcibly return null

     inorder on 1 calls it on null
     1) inorderElements = 1, the value is 1
        we call in order on 1s right, it is null and terminates
        the callstack for 1 ends, we forcibly return null

     the null terminates


*/
