// https://leetcode.com/problems/all-possible-full-binary-trees/description/
// difficulty: Medium
// tags: binary trees, recursion

// Problem
/*
Given an integer n, return a list of all possible full binary trees with n nodes. Each node of each tree in the answer must have Node.val == 0.

Each element of the answer is the root node of one possible tree. You may return the final list of trees in any order.

A full binary tree is a binary tree where each node has exactly 0 or 2 children.
*/

// Solution
/*
For a given amount of nodes left, say 7, we can make a certain list of trees of size 5. The list would be:

1) what if the left subtree is of size 1, right is size 5
2) what if the left subtree is of size 3, right is size 3
3) left is size 5, right is size 1

etc

And for each case, we consider all possible left and right subtrees of their repsective sizes.

This generates a recurrence relationship. The way I implemented it does create frankenstein trees (multiple nodes across trees pointing to the same child), which could easily be fixed by serializing and deserializing trees properly.

Also, we could memoize lists of subtrees. Also it is impossible to have a tree with an even amount of nodes, but the code will never create anything for those.
*/

var allPossibleFBT = function (n) {
  /*
    say we want to build a tree, n left nodes. say n is initially 5, meaning nLeft is 4 after we make a root node.

    what we want is to:

    make a tree with every left subtree of size 1, and every right subtree of size 3
    make a tree with every left subtree of size 3, and every right subtree of size 1

    then return that list

    the base case is a tree of size 1 is a node
    */
  function build(nLeft) {
    if (nLeft === 1) {
      return [new TreeNode(0)];
    }

    const treesForThis = [];

    for (let leftSize = 1; leftSize < nLeft; leftSize += 2) {
      const leftTreeList = build(leftSize);
      const rightTreeList = build(nLeft - leftSize - 1);
      for (const leftSubtree of leftTreeList) {
        for (const rightSubtree of rightTreeList) {
          const newRoot = new TreeNode(0);
          newRoot.left = leftSubtree;
          newRoot.right = rightSubtree;
          treesForThis.push(newRoot);
        }
      }
    }

    return treesForThis;
  }

  return build(n);
};
