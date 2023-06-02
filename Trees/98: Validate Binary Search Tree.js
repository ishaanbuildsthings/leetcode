// https://leetcode.com/problems/validate-binary-search-tree/description/
// Difficulty: Medium
// tags: bst, inorder traversal

// Solution 1, O(n) time and O(n) space, inorder traversal
/*
An inorder traversal of a valid BST yields a strictly increasing sequence. Iterate in in-order and validate the pattern.
*/

var isValidBST = function (root) {
  let currentNum = -Infinity;

  function dfs(node) {
    if (!node) return true;

    dfs(node.left);
    if (node.val <= currentNum) {
      return false;
    }
    currentNum = node.val;
    dfs(node.right);
  }

  return dfs(root);
};

// Solution 2, O(n) time and O(n) space, inorder traversal without array
/*
Instead of storing all the values in an array then validating it after, we can just track the current number and compare our new node with that. Writing the solution was a bit tricky, it's easier to think about our objective of iterating as much left as possible, after we hit null we validate the current number, then we travel right. We use the callstacks to bubble back up. Again, I think of inorder traversal as one node pointing into two nulls, rather than a node pointing to two other nodes.
*/

var isValidBST = function (root) {
  let currentNum = -Infinity;

  // objective is to do an inorder traversal, comparing values
  function dfs(node) {
    // if we are null, return true, since that is valid
    if (!node) return true;

    // if we arent null, keep iterating to the left as much as possible, as the first node we read should be the leftmost child
    if (!dfs(node.left)) return false;
    /* here we can't go left anymore as we hit null */

    // if our leftmost child node is not strictly increasing, we return false
    if (node.val <= currentNum) {
      return false;
    }
    /* here, our leftmost child was strictly increasing, we update the current value */

    currentNum = node.val;

    // now we need to go right
    if (!dfs(node.right)) return false;

    return true; // if it passes all the checks, it is a valid BST
  }

  return dfs(root);
};
