// https://leetcode.com/problems/construct-binary-tree-from-inorder-and-postorder-traversal/description/
// Difficulty: Medium
// tags: inorder, postorder, recursion

// Problem
/*
Given two integer arrays inorder and postorder where inorder is the inorder traversal of a binary tree and postorder is the postorder traversal of the same tree, construct and return the binary tree.
*/

// Solution, O(n) time and O(n) space.
// We take O(n) time as we recurse on each element once. The callstack takes the height's space, but creating the mapping takes n space and time.
/*
We know for a given postorder traversal, the last value is the root. We also know that some elements to the left of that may comprise its right subtree, and then elements to the left of that may comprise its left subtree. We lookup in the inorder traversal to see how many elements are to the left and right, and recurse accoridngly, using indices to track the portions of valid regions remaining.

    consider:
    in: 9, 3, 15, 20, 7
    post: 9, 15, 7, 20, 3
    Here, we know 3 is the root, there is 1 element to the left, and 3 to the right.
    The right subtree will start with 20. To know how many elements are on the left and right of 20, we have to use the reduced range from the in traversal, which is [15, 20, 7.]

  We terminate when rightPost < leftPost. This is because by default, rightPost is 1 less than the previous rightPost. leftPost is based on how many elements we had to the right of something. If we have no elements to the right, then leftPost ends up crossing with rightPost, and we terminate.

  We cannot terminate when rightPost === leftPost (by returning a single TreeNode). This is because if our root starts out as missing one child, when it recurses to that child, it will recurse forever.
*/

var buildTree = function (inorder, postorder) {
  const mapping = {}; // maps numbers in the inorder traversal to the index they occur at, so we can look it up instantly for future calls
  for (let i = 0; i < inorder.length; i++) {
    mapping[inorder[i]] = i;
  }

  // takes in the indices for the ranges for both traversals. We need this because:
  /*
    consider:
    in: 9, 3, 15, 20, 7
    post: 9, 15, 7, 20, 3
    Here, we know 3 is the root, there is 1 element to the left, and 3 to the right.
    The right subtree will start with 20. To know how many elements are on the left and right of 20, we have to use the reduced range from the in traversal, which is [15, 20, 7.]
    */
  function recurse(leftPost, rightPost, leftIn, rightIn) {
    if (rightPost < leftPost) {
      return null;
    }

    const root = new TreeNode(postorder[rightPost]); // the root is always the last element in the postorder traversal
    const rootIndex = mapping[root.val]; // the index inside the inorder traversal
    const numElementsToLeft = rootIndex - leftIn;
    const numElementsToRight = rightIn - rootIndex;

    // right region for postorder
    const rightIndexRightRegion = rightPost - 1;
    const leftIndexRightRegion =
      rightIndexRightRegion - (numElementsToRight - 1);

    // left region for postorder
    const rightIndexLeftRegion = leftIndexRightRegion - 1;
    const leftIndexLeftRegion = rightIndexLeftRegion - (numElementsToLeft - 1);

    // right region for inorder
    const leftIndexRightRegionInorder = rootIndex + 1;
    const rightIndexRightRegionInorder =
      leftIndexRightRegionInorder + numElementsToRight - 1;

    // left region for inorder
    const rightIndexLeftRegionInorder = rootIndex - 1;
    const leftIndexLeftRegionInorder =
      rightIndexLeftRegionInorder - numElementsToLeft + 1;

    root.left = recurse(
      leftIndexLeftRegion,
      rightIndexLeftRegion,
      leftIndexLeftRegionInorder,
      rightIndexLeftRegionInorder
    );
    root.right = recurse(
      leftIndexRightRegion,
      rightIndexRightRegion,
      leftIndexRightRegionInorder,
      rightIndexRightRegionInorder
    );

    return root;
  }

  return recurse(0, postorder.length - 1, 0, inorder.length - 1);
};
