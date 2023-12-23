// https://leetcode.com/problems/binary-tree-level-order-traversal/description/
// Difficulty: Medium
// tags: bfs

// Solution, O(n) time and O(n) space, as we may be holding nodes in the deque

/*
Do a BFS with a deque. Iterate over level by level by tracking the exact length of the deque, adding answers to the result.
*/

var levelOrder = function (root) {
  if (!root) return [];

  const result = [];

  const queue = new Deque();
  queue.push(root);

  while (queue.size() > 0) {
    const length = queue.size(); // length of the previous row
    const level = [];
    for (let i = 0; i < length; i++) {
      const node = queue.shift(); // O(1) for deque
      level.push(node.val);
      if (node.left) {
        queue.push(node.left);
      }
      if (node.right) {
        queue.push(node.right);
      }
    }
    result.push(level);
  }

  return result;
};

class Deque {
  constructor() {
    this.head = 0;
    this.tail = -1;
    this.storage = {};
  }

  push(val) {
    this.tail++;
    this.storage[this.tail] = val;
  }

  pop(val) {
    if (!(this.tail in this.storage)) {
      return null;
    }

    const popped = this.storage[this.tail];
    this.tail--;
    return popped;
  }

  shift() {
    if (!(this.head in this.storage)) {
      return null;
    }

    const popped = this.storage[this.head];
    this.head++;
    return popped;
  }

  unshift(val) {
    this.head--;
    this.storage[this.head] = val;
  }

  size() {
    return this.tail - this.head + 1;
  }
}
