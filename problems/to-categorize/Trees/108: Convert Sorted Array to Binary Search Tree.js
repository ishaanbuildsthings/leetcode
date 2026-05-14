// https://leetcode.com/problems/convert-sorted-array-to-binary-search-tree/description/
// tags: bst, recursion

// Problem
/*
Given an integer array nums where the elements are sorted in ascending order, convert it to a
height-balanced binary search tree.
*/

// Solution, O(n) time as we visit each element once, and O(log n) space for the callstack.
// Take the list, and get the middle value. That is our root node. Recurse on the left and right. We use pointers so we don't need to duplicate the array each time.

var sortedArrayToBST = function (nums) {
  // takes in the left and right pointers, denoting the range from which we must construct the BST.
  function recurse(l, r) {
    if (r < l) {
      return null;
    }
    const m = Math.floor((r + l) / 2);
    const root = new TreeNode(nums[m]);
    const leftNode = recurse(l, m - 1);
    const rightNode = recurse(m + 1, r);
    root.left = leftNode;
    root.right = rightNode;

    return root;
  }

  return recurse(0, nums.length - 1);
};
