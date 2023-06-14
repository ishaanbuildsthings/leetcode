// https://leetcode.com/problems/minimum-absolute-difference-in-bst/description/
// Difficulty: Easy
// tags: inorder, recursion, bst

// Problem
/*
Given the root of a Binary Search Tree (BST), return the minimum absolute difference between the values of any two different nodes in the tree.
*/

// Solution 1, O(n) time and O(n) (height) space. Do an inorder traversal, which is monotonically increasing for a BST. Track the differences.

var getMinimumDifference = function (root) {
  let minDifference = Infinity;

  let prevValue = Infinity; // starts at infinity so our initial difference between the root and a non-existent previous value, is infinity

  function inorder(node) {
    if (!node) {
      return;
    }

    inorder(node.left);

    // process current node
    const difference = Math.abs(prevValue - node.val);
    minDifference = Math.min(minDifference, difference);
    prevValue = node.val;

    inorder(node.right);
  }

  inorder(root);

  return minDifference;
};

// Solution 2, O(n) time and O(n) (height) space. Bottom up recursion. This is a good solution! We recurse down to the bottom, then bubble up results with the smallest and largest values in a tree. We don't need two functions, we just use a tuple.

var getMinimumDifference = function (root) {
  let minimumDifference = Infinity;

  // gets the smallest and largest values for a given root
  function dfs(node) {
    /*
        a bit hacky, there are other ways to fix this, just by using more `if` statements to check or verify if a child is null, and if it is null, don't process it the same way. regardless, this works because:

        1) if a node is null, we will say its smallest value is infinity, and its largest is -infinity. therefore, when it bubbles up to the parent, the parent will not update its smallest or largest because of  those. aalso, the difference between the node's value and these infinities is infinity, so the reult doesn't get updated.
        */
    if (!node) {
      return [Infinity, -Infinity];
    }

    const [leftSmallest, leftLargest] = dfs(node.left);
    const [rightSmallest, rightLargest] = dfs(node.right);

    // compare the node with the largest value from its left subtree
    const diff1 = Math.abs(node.val - leftLargest);
    minimumDifference = Math.min(minimumDifference, diff1);

    // compare the node with the largest value from its right subtree
    const diff2 = Math.abs(node.val - rightSmallest);
    minimumDifference = Math.min(minimumDifference, diff2);

    const newLargest = Math.max(leftLargest, rightLargest, node.val);
    const newSmallest = Math.min(leftSmallest, rightSmallest, node.val);
    return [newSmallest, newLargest];
  }

  dfs(root);

  return minimumDifference;
};

// Solution 3, O(n) time and O(n) space. Really bad recursion with memoization.
/*
Create a map that maps a node to the smallest value in its tree, and do the same for the largest value. Iterate through all nodes, compare the node's value with the largest value in its left subtree, and the smallest value in its right subtree, updating the result if we need. This solution started from the top, recursing down in a weird way. This code was very inelegant and should not be used as a reference.
*/

var getMinimumDifference = function (root) {
  const smallestCache = new Map(); // maps nodes to the smallest values their subtrees contain
  /*
    this function will recurse throughout the tree, mapping nodes to the smallest values they contain in that tree.
    the idea is to both populate the mapping, and to recursively call the function, all in one function, unlike doing it in two functions (such as 543: Diameter of Binary Tree).

    Say we start at a root node:
       4
      / \
     2   6

    To solve for the smallest value 4 contains, we take the smallest value it's left subtree has, so we recurse on 2.

    At 2, we don't have a left child, so we return 2.

    Now we are back at 4, and we know the smallest value is 2. We recurse on 4's chilren, 2 and 6, because we want to solve for other nodes 2.

    When we get to node 2, we don't want to do repeated work. So we check if that node is already cached, and if so, we recurse on its children, and skip solving for 2.

    */
  function mapSmallest(node) {
    // edge case if initially called on a null node, or if we try to recurse onto the right child that doesn't exist, from the line where we have processed this node before
    if (!node) {
      return;
    }

    // terminal state, we have no left child
    if (!node.left) {
      smallestCache.set(node, node.val);
      // even if we don't have a left child, we still need to fill the cache for the right subtree
      mapSmallest(node.right);
      return node.val;
    }

    // if we have processed this node before, solve for the children and skip this
    if (smallestCache.has(node)) {
      mapSmallest(node.left);
      mapSmallest(node.right);
      return;
    }

    const smallest = mapSmallest(node.left);

    smallestCache.set(node, smallest);

    mapSmallest(node.left);
    mapSmallest(node.right);

    return smallest;
  }

  mapSmallest(root);

  const largestCache = new Map();
  function mapLargest(node) {
    if (!node) {
      return;
    }

    // terminal state, no right child
    if (!node.right) {
      largestCache.set(node, node.val);
      // even if we don't have a right child, we still need to fill the cache for the left subtree
      mapLargest(node.left);
      return node.val;
    }

    // if we have processed this node before, solve for the children and skip this
    if (largestCache.has(node)) {
      mapLargest(node.left);
      mapLargest(node.right);
      return;
    }

    const largest = mapLargest(node.right);

    largestCache.set(node, largest);

    mapLargest(node.left);
    mapLargest(node.right);

    return largest;
  }

  mapLargest(root);

  let minimumDifference = Infinity;

  // console.log(`smallest cache size is: ${smallestCache.size} largest is: ${largestCache.size}`);

  for (const node of smallestCache.keys()) {
    // console.log(`node is: ${node} with value: ${node.val}`);
    // compare the node with the largest value in its left subtree
    if (node.left) {
      const largestFromLeftSubtree = largestCache.get(node.left);
      const difference = Math.abs(node.val - largestFromLeftSubtree);
      minimumDifference = Math.min(minimumDifference, difference);
    }

    // compare the node with the smallest value in its right subtree
    if (node.right) {
      const smallestFromRightSubtree = smallestCache.get(node.right);
      const difference = Math.abs(node.val - smallestFromRightSubtree);
      minimumDifference = Math.min(minimumDifference, difference);
    }
  }

  return minimumDifference;
};
