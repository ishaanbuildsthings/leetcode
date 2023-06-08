// https://leetcode.com/problems/flip-equivalent-binary-trees/
// Difficulty: Medium
// tags: recursion

// Solution 1, O(n + m) time, O(n + m) space
// * Solution 2 is a bit nicer / more efficient
/*
DFS through each tree (n + m) time. For each tree, create a mapping of a node's value to a tuple of the children's values. Then compare each key in the mappings to ensure the tuples are the same or reversed. We also need to validate they are the same length, as if we iterate over the shorter one we might erronously have a match.
*/

var flipEquiv = function (root1, root2) {
  const mapping1 = {}; // maps values for nodes from root1, to a tuple of the values of their children, like 1 : [2, 3]
  const mapping2 = {};

  // bottom up
  function dfs(node, mapping) {
    if (!node) {
      return -1;
    }

    mapping[node.val] = [dfs(node.left, mapping), dfs(node.right, mapping)];

    return node.val;
  }

  dfs(root1, mapping1);
  dfs(root2, mapping2);

  if (Object.keys(mapping1).length !== Object.keys(mapping2).length)
    return false;

  for (const key in mapping1) {
    const tuple1 = mapping1[key];
    const tuple2 = mapping2[key];
    if (JSON.stringify(tuple1) === JSON.stringify(tuple2)) {
      continue;
    }

    const reversedTuple1 = [tuple1[1], tuple1[0]];
    if (JSON.stringify(reversedTuple1) === JSON.stringify(tuple2)) {
      continue;
    }

    return false;
  }

  return true;
};

// Solution 2, the nicer pure recursive solution, still O(n + m) ttime and O(n + m) space, but now the space is the heights rather than all nodes (since previously we stored mappings for all nodes).

/*
To compare two trees, first evaluate the simple cases. If both nodes are null, we have valid trees. If just one is null, we do not. If we have two nodes, but their values are different, it is still invalid.

If we have two nodes that have the same values, then we need to recurse down. We have two possible ways that make it valid. If tree1 left child is flip equivalent to tree2 left child, and tree1 right child is flip equivalent to tree2 right child, then tree1 is flip equivalent to tree2.

But, we could also flip them, so we need to check the flipped orientation as well.
*/

var flipEquiv = function (root1, root2) {
  function dfs(node1, node2) {
    // two null nodes are the same
    if ((node1 === null) & (node2 === null)) {
      return true;
    }

    // if just one node is null, they are not the same
    if (!node1 || !node2) {
      return false;
    }
    /* here both nodes are not null */

    // if the nodes share different values, we cannot have a flip equivlant tree
    if (node1.val !== node2.val) {
      return false;
    }
    /* here both nodes have the same value */

    const notFlipped =
      dfs(node1.left, node2.left) && dfs(node1.right, node2.right);
    const flipped =
      dfs(node1.left, node2.right) && dfs(node1.right, node2.left);
    return notFlipped || flipped;
  }

  return dfs(root1, root2);
};
