// https://leetcode.com/problems/validate-binary-search-tree/description/
// Difficulty: Medium
// tags: bst, inorder traversal

// Solution 1, O(n) time and O(n) (height) space, inorder traversal without array
/*
Instead of storing all the values in an array then validating it after, we can just track the current number and compare our new node with that. Writing the solution was a bit tricky, it's easier to think about our objective of iterating as much left as possible, after we hit null we validate the current number, then we travel right. We use the callstacks to bubble back up. Again, I think of inorder traversal as one node pointing into two nulls, rather than a node pointing to two other nodes.

An easy way to think about it is a binary tree is valid if the left subtree is valid, the middle node is inorder relative to the biggest element from the left subtree, and the right subtree is valid. This recurses down until the base case of null.
*/

var isValidBST = function (root) {
  let currentNum = -Infinity;

  // objective is to determine if a subproblem is a valid bst
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

// Solution 2, DFS with ranges, O(n) time and O(n) space
/*
We cannot naively compare a node to its parent, because
   5
    \
     6
    /
   3

  Is not valid, as all numbers to the right of 5 need to be bigger than 5.

  Because of this, we keep a range of the bounds, and change the range based on which direction we are moving.

*/
var isValidBST = function (root) {
  function dfs(node, lowerBound, upperBound) {
    if (!node) return true;

    // if we are outside the range, return false
    if (!(node.val > lowerBound) || !(node.val < upperBound)) {
      return false;
    }

    // check the left subtree, creating a new upperbound
    const leftResult = dfs(node.left, lowerBound, node.val);
    // check the right
    const rightResult = dfs(node.right, node.val, upperBound);

    return leftResult && rightResult;
  }

  return dfs(root, -Infinity, Infinity);
};
