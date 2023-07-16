// https://leetcode.com/problems/unique-binary-search-trees/description/
// Difficulty: Medium
// Tags: dynamic programming 2d

// Problem
/*
Given an integer n, return the number of structurally unique BST's (binary search trees) which has exactly n nodes of unique values from 1 to n.
*/

// Solution, O(n^3) time and O(n^2) space
/*
We can store a memo of [l, r] which determines how many trees we can make in that range. Then for a given tree, we pick a node, and use the number of left subtrees times the number of right.

Since there are n^2 states, and each state takes n time, the complexity is n^3.
*/

var numTrees = function (n) {
  // memo[l][r] stores how many subtrees can be constructed in some remaining range
  const memo = new Array(n + 1).fill().map(() => new Array(n + 1).fill(-1));
  function recurse(l, r) {
    // base case, remember nulls are valid subtrees, if we check the left of 1, we need to consider the left to be a valid subtree otherwise the total amount of trees is 0
    if (l > r) {
      return 1;
    }

    if (memo[l][r] !== -1) {
      return memo[l][r];
    }

    let numTreesForThisRange = 0;

    for (let i = l; i <= r; i++) {
      const leftAmount = recurse(l, i - 1);
      const rightAmount = recurse(i + 1, r);
      const totalForThisRoot = leftAmount * rightAmount;
      numTreesForThisRange += totalForThisRoot;
    }

    memo[l][r] = numTreesForThisRange;
    return numTreesForThisRange;
  }

  return recurse(1, n);
};
