// https://leetcode.com/problems/subtree-of-another-tree/description/
// Difficulty: Easy

// Problem
/*
Given the roots of two binary trees root and subRoot, return true if there is a subtree of root with the same structure and node values of subRoot and false otherwise.

A subtree of a binary tree tree is a tree that consists of a node in tree and all of this node's descendants. The tree tree could also be considered as a subtree of itself.
*/

// Solution 1, serialization. O(n+m) time and O(n+m) space. Iterate over the main tree (any order) and serialize it by adding characters for the null leafs, to make sure the tree is appropriate distinct. We also have to add delimiters for each value, for instance 22 could be interpreted as two nodes each with value 2, or one node with value 22. A delimiter like 2|2 makes it clear. We take n+m time to serialize both the main tree and potential subtree. Then we iterate across n, doing m string checks using a rolling hash, so still n time (though n*m worst case).
// I didn't implement the rolling hash here and just used naive checks, but it could be done.

var isSubtree = function (root, subRoot) {
  function recurse(node, arr) {
    if (!node) {
      arr.push("|");
      arr.push("@");
      return;
    }
    arr.push("|");
    arr.push(node.val);
    recurse(node.left, arr);
    recurse(node.right, arr);
  }
  let rootArray = [];
  recurse(root, rootArray);
  const rootStr = rootArray.join("");

  let subRootArray = [];
  recurse(subRoot, subRootArray);
  const subRootStr = subRootArray.join("");

  for (let i = 0; i < rootStr.length; i++) {
    const substring = rootStr.slice(i, i + subRootStr.length);
    if (substring === subRootStr) {
      return true;
    }
  }

  return false;
};

// Solution 2, recursive DFS, O(n*m) time as for each node of n we do m checks. O(n+m) space as worst case we recurse down both trees.
/*
Recurse down the main tree, for each node, do a full check to see if it is equal to the given subroot, using the helper function isSameTree2.
*/

const isSubtree2 = function (root, subRoot) {
  if (!root) return false; // nothing can be found in a null node
  if (isSameTree2(root, subRoot)) return true; // we find a match
  return isSubtree2(root.left, subRoot) || isSubtree2(root.right, subRoot);
};

const isSameTree2 = function (node1, node2) {
  if (!node1 && !node2) return true; // two null nodes are the same
  if (!node1 && node2) return false; // a single null is not the same
  if (node1 && !node2) return false;
  if (node1.val !== node2.val) return false; // even if we have two nodes, if they are different it is false

  return (
    isSameTree2(node1.left, node2.left) && isSameTree2(node1.right, node2.right)
  ); // if everything checks out, recurse down to the children
};

// Solution 3, iterative DFS, O(n*m) time and O(n+m) space
/*
Iterate down the main tree, for each node, do a full check to see if it is equal to the given subroot, using the helper function isSameTree3.
*/

const isSubtree3 = function (root, subRoot) {
  const stack = [root]; // iterative DFS
  while (stack.length > 0) {
    const node = stack.pop();
    // don't process null nodes
    if (!node) {
      continue;
    }
    // if we found a match, return true
    if (isSameTree3(node, subRoot)) {
      return true;
    }
    // if there is no match, continue the dfs
    stack.push(node.left);
    stack.push(node.right);
  }
  return false;
};

const isSameTree3 = function (node1, node2) {
  if (!node1 && !node2) return true; // two null nodes are the same
  if (!node1 && node2) return false; // a single null is not the same
  if (node1 && !node2) return false;
  if (node1.val !== node2.val) return false; // even if we have two nodes, if they are different it is false

  return (
    isSameTree3(node1.left, node2.left) && isSameTree(node1.right, node2.right)
  ); // if everything checks out, recurse down to the children
};
