// https://leetcode.com/problems/count-univalue-subtrees/description/
// Difficulty: Medium
// tags: trees, bottom up recursion

// Problem
/*
Given the root of a binary tree, return the number of uni-value
subtrees.

A uni-value subtree means all nodes of the subtree have the same value.
*/

// Solution, O(n) time and O(h) space.

/*
Define a DFS function that returns if it is univalued, and how many univalued subtrees it has. We need to track if it is univalued, rather than just comparing a node to its children values, because there may be grandchildren that have different values. DFS down to the bottom, and give a base case if null. If a leaf node, that is also a base case. Otherwise, handle certain cases based on the children results.
*/
var countUnivalSubtrees = function (root) {
  // returns if the subtree is univalued, as well as the count of univalue subtrees in it
  function dfs(node) {
    // if there is no node, base case
    if (!node) {
      return [true, 0];
    }

    const [leftUnivalue, leftCount] = dfs(node.left);
    const [rightUnivalue, rightCount] = dfs(node.right);

    // if we have neither child, we form a univalue subtree of 1
    if (!node.right && !node.left) {
      return [true, 1];
    }

    // if we have just a left child
    else if (node.left && !node.right) {
      // if we match with the left child, and the left child was univalued, we get an extra subtree
      if (node.left.val === node.left && leftUnivalue) {
        return [true, leftCount + 1];
      }

      // if we either don't match with the left, or the left wasn't univalued, we don't get an extra
      return [false, leftCount];
    }

    // if we have just a right child
    else if (node.right && !node.left) {
      if (node.right.val === node.val && rightUnivalue) {
        return [true, rightCount + 1];
      }
      return [false, rightCount];
    }

    // if we have both children, we gain a tree if both are univalued, and we match with both
    else {
      if (
        node.val === node.left.val &&
        node.val === node.right.val &&
        leftUnivalue &&
        rightUnivalue
      ) {
        return [true, 1 + leftCount + rightCount];
      }
      return [false, leftCount + rightCount];
    }
  }

  return dfs(root)[1];
};

/*
       1
     1    1
   5  5  N 5


*/
