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
