// https://leetcode.com/problems/maximum-depth-of-binary-tree/description/
// Difficulty: Easy
// tags: binary tree, recursion, dfs, bfs

// Problem
/*
Simplified: Find the maximum depth of a binary tree
*/

// Solution, O(n) time as we iterate through every node, and O(n) space as we can have a callstack that is the depth of the tree, which is worst case all nodes. Create a max depth variable, DFS down the tree, and update the variable.
// * Solution 2 has the slicker version that avoids the recurse sub-function, since we don't need the max depth variable anymore as we embed the number directly in the return statement. (technically we never needed the maxDepth variable in the closure as it could go outside the function as well but that wouldn't be good practice)
// * Solution 3, iterative BFS

var maxDepth = function (root) {
  let maxDepth = 0;

  function recurse(node, depth) {
    // edge case if the entire tree is null
    if (!node) {
      return;
    }

    maxDepth = Math.max(maxDepth, depth);

    if (node.left) {
      recurse(node.left, depth + 1);
    }

    if (node.right) {
      recurse(node.right, depth + 1);
    }
  }

  recurse(root, 1);
  return maxDepth;
};

// Solution 2, the slicker DFS that avoids the recurse function

var maxDepth = function (root) {
  if (!root) {
    return 0;
  }
  return Math.max(1 + maxDepth(root.left), 1 + maxDepth(root.right));
};

// Solution 3, iterative BFS with a dequeue, time is still O(n), space is O(n) which is the max width of the tree, which can be n
/*
For a given level, iterate through the entire level, shifting the elements off the deque and adding their existing children. After all that is done, increment the depth, since the depth increases for every level.
*/
var maxDepth = function (root) {
  if (!root) {
    return 0;
  }

  let depth = 0;
  const fakeDeque = [root];

  while (fakeDeque.length > 0) {
    const initialLength = fakeDeque.length;
    // will always process the entire next row
    for (let i = 0; i < initialLength; i++) {
      const node = fakeDeque.shift(); // O(1) for a real deque
      if (node.left) {
        fakeDeque.push(node.left);
      }
      if (node.right) {
        fakeDeque.push(node.right);
      }
    }
    depth++;
  }
  return depth;
};

// Solution 4, iterative DFS using a stack, time is O(n) and space is O(n) (depth). Uses a stack to add elements. Since we cannot bubble up like in recursion, and preserve the depth at that level, we need tuples to also store the depth of current elements, as otherwise we don't have certainty of the depth of the node we are at.

var maxDepth = function (root) {
  if (!root) {
    return 0;
  }

  let maxDepth = 0;
  const stack = [[root, 1]];

  while (stack.length > 0) {
    const tuple = stack.pop();
    const node = tuple[0];
    const depth = tuple[1];
    maxDepth = Math.max(maxDepth, depth);
    if (node.left) {
      stack.push([node.left, depth + 1]);
    }
    if (node.right) {
      stack.push([node.right, depth + 1]);
    }
  }
  return maxDepth;
};

// Solution 5, recursive DFS with size as parameter
var maxDepth = function (root, size = 0) {
  if (!root) return size;

  return Math.max(
    maxDepth(root.left, size + 1),
    maxDepth(root.right, size + 1)
  );
};
