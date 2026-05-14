// https://leetcode.com/problems/construct-binary-tree-from-preorder-and-postorder-traversal/description/
// Difficulty: Medium
// tags: recursion, preorder, postorder

// Problem
/*
Given two integer arrays, preorder and postorder where preorder is the preorder traversal of a binary tree of distinct values and postorder is the postorder traversal of the same tree, reconstruct and return the binary tree.

If there exist multiple answers, you can return any of them.
*/

// Solution, O(n) time and O(n) space for the mapping.
/*
A bit of a nightmare problem to implement the linear solution for, because we have to deal with so many indices. I'm not 100% on the details of my solution, it ended up working but I became tired to fully understand why I needed 2 base cases. I believe it should be doable with just 1 base case.

The overall gist is that:

pre: 1, 2, 4, 5, 3, 6, 7
post: 4, 5, 2, 6, 7, 3, 1

We know 1 is our root node. We can always say 2 is our left subtree root. This is because a preorder + postorder cannot uniquely serialize (consider a tree of two, a root + either a left or right child, they produce the same result). The question just asks us to return 1 tree. So we know 2 is our left subtree root. We find 2 in post. The left region [4, 5, 2] therefore composes the left subtree, as the last element of the postorder traversal is the root. We recurse as such.
*/

var constructFromPrePost = function (preorder, postorder) {
  const postIndices = {}; // maps postorder numbers to where they occur, so we can look them up later
  for (let i = 0; i < postorder.length; i++) {
    const num = postorder[i];
    postIndices[num] = i;
  }

  // the boundaries of the ranges we are considering
  function construct(preL, preR, postL, postR) {
    if (preR < preL) {
      return null;
    }

    if (preR === preL) return new TreeNode(preorder[preL]);

    const rootNode = new TreeNode(preorder[preL]);

    /*
        pre: 1, 2, 4, 5, 3, 6, 7
        post: 4, 5, 2, 6, 7, 3, 1

        1 is the root. We will say 2 is the child of the left subtree. We find 2 in post. The left subtree consists of [4, 5, 2]. The right subtree therefore consists of [3, 6, 7]. Say we solve for the right subtree. 3 is the root. 6 is its left child. We find 3 in post. The left subtree consists of just [6], which is based on the left boundary from postL.
        */

    const index = postIndices[preorder[preL + 1]]; // find where that left child exists in post

    // left child
    const elementsInLeftSubtree = index - postL + 1;
    const leftChildPreL = preL + 1;
    const leftChildPreR = leftChildPreL + elementsInLeftSubtree - 1;

    const leftChildPostL = postL;
    const leftChildPostR = index;

    rootNode.left = construct(
      leftChildPreL,
      leftChildPreR,
      leftChildPostL,
      leftChildPostR
    );

    // right child
    const rightChildPreL = leftChildPreR + 1;
    const rightChildPreR = preR;

    const rightChildPostL = index + 1;
    const rightChildPostR = postR - 1;

    rootNode.right = construct(
      rightChildPreL,
      rightChildPreR,
      rightChildPostL,
      rightChildPostR
    );

    return rootNode;
  }

  return construct(0, preorder.length - 1, 0, postorder.length - 1);
};
