// https://leetcode.com/problems/binary-tree-zigzag-level-order-traversal/description/
// Difficulty: Medium
// tags: bfs

// Problem
/*
Given the root of a binary tree, return the zigzag level order traversal of its nodes' values. (i.e., from left to right, then right to left for the next level and alternate between).
*/

// Solution, O(n) time and O(n) space for the deque. Assuming O(1) shift operation with a real deque.

/*
Do level order traversal, and each level reverse the direction of the level. This is a bit more of a naive solution, you could probably do something like change the direction you read or add children to the deque, based on which level you are on.
*/

var zigzagLevelOrder = function (root) {
  // edge case
  if (!root) {
    return [];
  }

  const deque = [root]; // fake deque, pretending O(1) shift
  let direction = "right"; // we start by moving to the right
  const result = [];

  // level order traversal
  while (deque.length > 0) {
    const level = [];

    // we have some amount of nodes from the previous level, iterate over all of those nodes, adding their children to the deque, and updating the result
    const length = deque.length;

    // iterate over a level, add all the elements to `level`, and push their children to the deque
    for (let i = 0; i < length; i++) {
      const node = deque.shift();
      level.push(node.val);
      if (node.left) {
        deque.push(node.left);
      }
      if (node.right) {
        deque.push(node.right);
      }
    }

    if (direction === "right") {
      result.push(level);
      direction = "left";
    } else {
      result.push(level.reverse());
      direction = "right";
    }
  }

  return result;
};
