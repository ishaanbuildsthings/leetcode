// https://leetcode.com/problems/construct-binary-tree-from-preorder-and-inorder-traversal/description/
// Difficulty: Medium
// tags: binary tree, preorder, inorder, recursion

// Problem
/*
Given two integer arrays preorder and inorder where preorder is the preorder traversal of a binary tree and inorder is the inorder traversal of the same tree, construct and return the binary tree.

Input: preorder = [3,9,20,15,7], inorder = [9,3,15,20,7]
Output: [3,9,20,null,null,15,7]
*/

// Solution, O(n^2) time and O(n^2) space
// * solution 2 is done in n time and n space, using indices to represent portions of the array, and a mapping to instantly lookup indices in `inorder`
/*
Consider the traversals:
preorder = [3,9,20,15,7], inorder = [9,3,15,20,7]

We know at the start, 3 is the root, because it is the first preorder. Then, some elements may exist to the left of 3, and some to the right. We cannot tell from the preorder. But if we look at the inorder, we know, based on where the 3 is, that 1 element occured to the left of 3, and 3 elements occured to the right of 3.

If 1 element is to the left of 3, that means when we look at preorder, the next 1 element(s) should be treated as the left subtree. The 3 element(s) after that should be treated as the right.

preorder: [3, 9, 20, 15, 7]
           ^root
              [9] = left subtree
                [20, 15, 7] = right subtree

So we recurse, by passing [9] as the preorder and [9] as the inorder. [20, 15, 17] as the preorder and [15, 20, 7] as the inorder.

For each node, we do a slice on a subarray which takes n time and space, in the worst case for a stick graph.
*/

var buildTree = function (preorder, inorder) {
  if (preorder.length === 0) {
    return null;
  }

  const newRootNode = new TreeNode(preorder[0]);
  const locationOfRoot = inorder.indexOf(preorder[0]);
  const leftPreorder = preorder.slice(1, 1 + locationOfRoot);
  const rightPreorder = preorder.slice(1 + locationOfRoot);

  newRootNode.left = buildTree(leftPreorder, inorder.slice(0, locationOfRoot));
  newRootNode.right = buildTree(
    rightPreorder,
    inorder.slice(locationOfRoot + 1)
  );

  return newRootNode;
};

// Solution 2

var buildTree = function (preorder, inorder) {
  // map numbers to their locations in `inorder`, so we don't have to do lookups later
  const inorderMapping = {};
  for (let i = 0; i < inorder.length; i++) {
    inorderMapping[inorder[i]] = i;
  }

  // represent index boundaries, inclusive
  function recurse(leftPre, rightPre, leftIn, rightIn) {
    // if the indices ever cross, we have no elements left
    if (rightPre < leftPre) {
      return null;
    }

    const newRootNode = new TreeNode(preorder[leftPre]);
    const locationOfRoot = inorderMapping[newRootNode.val];

    const elementsToLeftOfRoot = locationOfRoot - leftIn;

    const leftChildLeftBoundaryPre = leftPre + 1;
    const leftChildRightBoundaryPre = leftPre + elementsToLeftOfRoot;

    const rightChildLeftBoundaryPre = leftChildRightBoundaryPre + 1;
    const rightChildRightBoundaryPre = rightPre;

    const leftChildLeftBoundaryIn = leftIn;
    const leftChildRightBoundaryIn = locationOfRoot - 1;

    const rightChildLeftBoundaryIn = locationOfRoot + 1;
    const rightChildRightBoundaryIn = rightIn;

    newRootNode.left = recurse(
      leftChildLeftBoundaryPre,
      leftChildRightBoundaryPre,
      leftChildLeftBoundaryIn,
      leftChildRightBoundaryIn
    );
    newRootNode.right = recurse(
      rightChildLeftBoundaryPre,
      rightChildRightBoundaryPre,
      rightChildLeftBoundaryIn,
      rightChildRightBoundaryIn
    );

    return newRootNode;
  }

  return recurse(0, preorder.length - 1, 0, inorder.length - 1);
};
