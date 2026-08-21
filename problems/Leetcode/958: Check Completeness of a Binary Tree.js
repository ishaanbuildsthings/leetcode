// https://leetcode.com/problems/check-completeness-of-a-binary-tree/description/
// Difficulty: Medium
// tags: binary tree, bfs

// Problem

/*
Given the root of a binary tree, determine if it is a complete binary tree.

In a complete binary tree, every level, except possibly the last, is completely filled, and all nodes in the last level are as far left as possible. It can have between 1 and 2h nodes inclusive at the last level h.
*/

// Solution 1, O(n) time and O(n) space
/*
I found the max depth of the tree, then did a BFS. If we are ever missing a child, we are not allowed more children on that level. If we are on the last level, we can skip everything since we know that level is fine (the previous level would have handled if the last level was wrong).
*/
/*
 *
 Solution 2 is a bit easier to code and understanding, sol 1 is just what I wrote initially. It is still n time and n space. The pseudocode for solution 2 is:
 * Do a BFS traversal, maintaining a track of the previous node. If the previous node was ever null, and we get a non-null, return false, because that implies a gap either in the level, or a level that ended with nulls and then a new level. For this bfs, we need to add the nulls to the deque so we can process them.

 * We could even do a BFS and store things in an array, then check for gaps. The above is just the `more constant` space solution so to speak, as we memoize the prior value.
 */

// Solution 1 code

function getMaxDepth(node) {
  if (!node) {
    return 0;
  }

  return 1 + Math.max(getMaxDepth(node.left), getMaxDepth(node.right));
}

var isCompleteTree = function (root) {
  // if we ever don't have a left child, we will fail it we have a right child, or any more nodes on that level
  // if we ever don't have a right child, we will fail if we have any more nodes on that level
  const deque = [root]; // fake deque

  const maxDepth = getMaxDepth(root);
  let level = 1;

  while (deque.length > 0) {
    const length = deque.length;

    // if we are on the last depth, we are fine, the elements cannot be out of order because they were validated by the prior level
    if (level === maxDepth) {
      return true;
    }

    let moreChildrenAllowedThisLevel = true;

    for (let i = 0; i < length; i++) {
      const node = deque.shift(); // pretend O(1)

      // if we are missing a child, and are not on the last COMPLETE level, we cannot have a complete tree
      if ((!node.left || !node.right) && level !== maxDepth - 1) {
        return false;
      }

      // if we don't have a left child, we cannot have more children in that row
      if (!node.left) {
        moreChildrenAllowedThisLevel = false;
      }
      // if we do have a left child, either add it or fail, if we weren't allowed more children from before
      else if (node.left) {
        if (!moreChildrenAllowedThisLevel) {
          return false;
        }
        deque.push(node.left);
      }

      // if we don't have a right child, we cannot have more children in that row
      if (!node.right) {
        moreChildrenAllowedThisLevel = false;
      }
      // if we do have a right child, either add it or fail, if we weren't allowed more children from before
      else if (node.right) {
        if (!moreChildrenAllowedThisLevel) {
          return false;
        }
        deque.push(node.right);
      }
    }

    level++;
  }

  return true;
};
