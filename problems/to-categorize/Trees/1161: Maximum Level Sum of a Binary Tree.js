// https://leetcode.com/problems/maximum-level-sum-of-a-binary-tree/description/
// Difficulty: Medimum
// tags: bfs

// Problem
/*
Simplified:
Input: root = [1,7,0,7,-8,null,null]
Output: 2
Explanation:
Level 1 sum = 1.
Level 2 sum = 7 + 0 = 7.
Level 3 sum = 7 + -8 = -1.
So we return the level with the maximum sum which is level 2.

Detailed:
Given the root of a binary tree, the level of its root is 1, the level of its children is 2, and so on.

Return the smallest level x such that the sum of all the values of nodes at level x is maximal.
*/

// Solution, O(n) time (with real deque) and O(n) space. Do a BFS, tracking the level, current max sum, and updating the result as needed.

var maxLevelSum = function (root) {
  const deque = [root];

  let maxSum = -Infinity;
  let resultLevel;

  let currentLevel = 0;
  while (deque.length > 0) {
    currentLevel++; // we start initially at level 1
    const length = deque.length;
    let sum = 0;
    for (let i = 0; i < length; i++) {
      const node = deque.shift(); // pretend O(1)
      sum += node.val;

      if (node.left) {
        deque.push(node.left);
      }

      if (node.right) {
        deque.push(node.right);
      }
    }

    if (sum > maxSum) {
      resultLevel = currentLevel;
      maxSum = sum;
    }
  }

  return resultLevel;
};
