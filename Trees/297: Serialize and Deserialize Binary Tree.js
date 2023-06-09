// https://leetcode.com/problems/serialize-and-deserialize-binary-tree/description/
// Difficulty: Hard
// tags: binary tree, preorder

// Problem
/*
Simplified: We are given a binary tree. We need to serialize it, then deserialize it to produce the same tree.

Detailed:
Serialization is the process of converting a data structure or object into a sequence of bits so that it can be stored in a file or memory buffer, or transmitted across a network connection link to be reconstructed later in the same or another computer environment.

Design an algorithm to serialize and deserialize a binary tree. There is no restriction on how your serialization/deserialization algorithm should work. You just need to ensure that a binary tree can be serialized to a string and this string can be deserialized to the original tree structure.

Clarification: The input/output format is the same as how LeetCode serializes a binary tree. You do not necessarily need to follow this format, so please be creative and come up with different approaches yourself.
*/

// Solution, O(n) for serialization and O(n) for deserialization
/*
To serialize, do a preorder traversal along with nulls, which uniquely serializes. Return the stringified traversal.

To deserialize:

[1, null, null]
recurse(0)

1) take the 0th value and create a node
2) create a left subtree, starting at i+1
3) that left subtree terminates at a certain index, now we create a right subtree, starting past that
4) that right subtree terminates
5) return the node
*/

var serialize = function (root) {
  const preorderTraversal = preorder(root);
  const serialization = JSON.stringify(preorderTraversal);
  return serialization;
};

function preorder(root) {
  const result = [];

  function dfs(node) {
    if (!node) {
      result.push(null);
      return;
    }

    result.push(node.val);
    dfs(node.left);
    dfs(node.right);
  }

  dfs(root);

  return result;
}

/*
[1, null, null]
recurse(0)

1) take the 0th value and create a node
2) create a left subtree, starting at i+1
3) that left subtree terminates at a certain index, now we create a right subtree, starting past that
4) that right subtree terminates
5) return the node


*/
var deserialize = function (data) {
  const arr = JSON.parse(data);

  function recurse(i) {
    // if we are at anull, return null and `i`, as `i` is the default ending index
    if (arr[i] === null) {
      return [null, i];
    }

    const newNode = new TreeNode(arr[i]);

    // leftIndex is the last index that was used for the left side
    const [leftNode, leftIndex] = recurse(i + 1);
    newNode.left = leftNode;

    const [rightNode, rightIndex] = recurse(leftIndex + 1);
    newNode.right = rightNode;

    return [newNode, rightIndex];
  }

  return recurse(0)[0];
};
