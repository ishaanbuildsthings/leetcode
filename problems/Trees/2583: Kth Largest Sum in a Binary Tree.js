// https://leetcode.com/problems/kth-largest-sum-in-a-binary-tree/description/
// Difficulty: Medium
// tags: binary tree, bfs

// Problem
/*
You are given the root of a binary tree and a positive integer k.

The level sum in the tree is the sum of the values of the nodes that are on the same level.

Return the kth largest level sum in the tree (not necessarily distinct). If there are fewer than k levels in the tree, return -1.

Note that two nodes are on the same level if they have the same distance from the root.
*/

// Solution, O(n) time (with a real queue), O(n) space for the queue, O(levels log(levels)) time for the sort, O(levels) space for the sort, so the time can be O(n log n) for a linked list
// Just get the level sums, sort them, return the right one

var kthLargestLevelSum = function (root, k) {
  const levelSums = [];

  const queue = [root]; // fake queue

  while (queue.length > 0) {
    let sum = 0;
    const length = queue.length;
    for (let i = 0; i < length; i++) {
      const node = queue.shift();
      sum += node.val;
      if (node.left) {
        queue.push(node.left);
      }
      if (node.right) {
        queue.push(node.right);
      }
    }
    levelSums.push(sum);
  }

  levelSums.sort((a, b) => a - b);

  if (k > levelSums.length) {
    return -1;
  }

  return levelSums[levelSums.length - k];
};
