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
