// https://leetcode.com/problems/sum-root-to-leaf-numbers/description/
// Difficulty: Medium
// tags: binary tree, dfs

// Problem
/*
Simplified:
Input: root = [1,2,3]
Output: 25
Explanation:
The root-to-leaf path 1->2 represents the number 12.
The root-to-leaf path 1->3 represents the number 13.
Therefore, sum = 12 + 13 = 25.

Detailed
You are given the root of a binary tree containing digits from 0 to 9 only.

Each root-to-leaf path in the tree represents a number.

For example, the root-to-leaf path 1 -> 2 -> 3 represents the number 123.
Return the total sum of all root-to-leaf numbers. Test cases are generated so that the answer will fit in a 32-bit integer.

A leaf node is a node with no children.
*/

// Solution, O(n) time and O(n) (height) space from the recursive callstack
/*
Do dfs traversals, incrementing the current number as we descend. If a number has two null children, we add the sum once. Otherwise, we recurse in the relevant places.

There is also another style solution where for a node, we increment the value (so an initial root of 1 would increment from 0->1). Or a leaf of 2 would increment from 1->12. Then we sum the recurses on the children. If null, return 0.
*/

var sumNumbers = function (root) {
  let sum = 0;

  // iterates down maintain an accrual, when we have only nulls we terminate
  function dfs(node, accruedNum) {
    if (!node) {
      sum += accruedNum;
      return;
    }

    accruedNum *= 10;
    accruedNum += node.val;

    // if we don't have either child, just recurse once to get that accrual one time
    if (!node.left && !node.right) {
      dfs(node.left, accruedNum);
      return;
    }
    // if we only have the right child, only recurse there
    else if (!node.left) {
      dfs(node.right, accruedNum);
    }
    // if we only have the left child, only recurse there
    else if (!node.right) {
      dfs(node.left, accruedNum);
    }
    // if we have both children, recurse on both
    else {
      dfs(node.left, accruedNum);
      dfs(node.right, accruedNum);
    }
  }

  dfs(root, 0);

  return sum;
};
