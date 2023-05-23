// https://leetcode.com/problems/same-tree/editorial/
// Difficulty: Easy
// tags: recursion

// Problem
// Check if two trees are structurally the same (.left and .right match up, values match up)

// Solution, Time: O(min(p, q)), where p and q are the number of nodes in those trees. Space(min(p, q)), since worst case the trees are stick graphs. We use minimum since we cannot possibly recurse more than the smaller tree, as we would get a mismatch and immediately return.
/*
Make a recurse function (not needed, see second solution where the function itself is the recursive call). It compares a node from p with a node from q. If they are both null, it returns true, as there is a match. If one is null, it returns false as there is a mismatch. If both are nodes, it checks the values, and returns false if there is a mismatch. Then, if they're both nodes, it recurses on their left children, then their right children, and based on those results can return false if they're false. Only if neither was false does it mean we have a full tree match and can return true.
*/

// version with unnecessary closure, see version 2 for the slicker version
var isSameTree = function (p, q) {
  function recurse(nodeP, nodeQ) {
    // if only one node is null, return false
    if ((!nodeP && nodeQ) || (nodeP && !nodeQ)) {
      return false;
    }

    // if both nodes are null, return true
    if (!nodeP && !nodeQ) {
      return true;
    }
    // here, both nodes are non-null

    // if the nodes do not have the same value, return false
    if (nodeP.val !== nodeQ.val) {
      return false;
    }

    // check the left children
    if (recurse(nodeP.left, nodeQ.left) === false) {
      return false;
    }

    // check the right children
    if (recurse(nodeP.right, nodeQ.right) === false) {
      return false;
    }

    // if all passes succeed, return true
    return true;
  }

  return recurse(p, q);
};

// version without unnecessary closure
var isSameTree = function (nodeP, nodeQ) {
  // if only one node is null, return false
  if ((!nodeP && nodeQ) || (nodeP && !nodeQ)) {
    return false;
  }

  // if both nodes are null, return true
  if (!nodeP && !nodeQ) {
    return true;
  }
  // here, both nodes are non-null

  // if the nodes do not have the same value, return false
  if (nodeP.val !== nodeQ.val) {
    return false;
  }

  return (
    isSameTree(nodeP.left, nodeQ.left) && isSameTree(nodeP.right, nodeQ.right)
  );
};
