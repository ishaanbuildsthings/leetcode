// https://leetcode.com/problems/unique-binary-search-trees-ii/description/
// Difficulty: Medium
// Tags: dynamic programming 2d

// Problem
/*
Example:
Input: n = 3
Output: [[1,null,2,null,3],[1,null,3,2],[2,1,3],[3,1,null,null,2],[3,2,null,1]]

Detailed:
Given an integer n, return all the structurally unique BST's (binary search trees), which has exactly n nodes of unique values from 1 to n. Return the answer in any order.
*/

// Solution, O(n^6) (I am not sure this is fully right LOL), not sure about space. Would need to analyze the problem more in depth later.
/*
I think brute force actually worked for this problem due to n<=8, but we can also memoize serialized lists of valid subtrees for the range from l to r.

There are n^2 states, and for each state, we iterate n times. For each iteration, we iterate through n^2 configurations (I think), and do an n serialization.
*/

var generateTrees = function (n) {
  // memo[l][r] contains a serialized list of trees for that range, we can memoize for some problems, for instance if 2 is our root we can check all trees on the right of 2, if 1 is our root and 2 is a right child, we can reuse that result
  const memo = new Array(n + 1).fill().map(() => new Array(n + 1).fill(-1));

  // returns a list of all subtrees with the values from l to r
  function build(l, r) {
    if (l > r) {
      return [null];
    }

    if (l === r) {
      return [new TreeNode(l)];
    }

    if (memo[l][r] !== -1) {
      return JSON.parse(memo[l][r]);
    }

    const result = [];

    for (let rootNum = l; rootNum <= r; rootNum++) {
      const rootNode = new TreeNode(rootNum);
      const possibleLeftConfigurationsWithThisRoot = build(l, rootNum - 1);
      const possibleRightConfigurationsWithThisRoot = build(rootNum + 1, r);

      for (const leftConfig of possibleLeftConfigurationsWithThisRoot) {
        for (const rightConfig of possibleRightConfigurationsWithThisRoot) {
          rootNode.left = leftConfig;
          rootNode.right = rightConfig;
          result.push(JSON.parse(JSON.stringify(rootNode)));
        }
      }
    }

    memo[l][r] = JSON.stringify(result);
    return result;
  }

  return build(1, n);
};
