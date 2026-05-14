// https://leetcode.com/problems/find-duplicate-subtrees/description/
// Difficulty: Medium
// tags: preorder

// Problem
/*
Given the root of a binary tree, return all duplicate subtrees.

For each kind of duplicate subtrees, you only need to return the root node of any one of them.

Two trees are duplicate if they have the same structure with the same node values.
*/

// Solution 1, preorder traversal, O(n^2) time and O(n^2) space
// * Solution 2 is optimized
/*
Recurse and serialize subtrees. A subtree must reach the leaf nodes. Add the serialization to a hashmap with a count of how many times it has been seen already. If we have already seen it exactly once, add to the result. To serialize, we can use pre or postorder traversal to gain unique serialization, assuming we include nulls. This does not work for inorder.

I did an inorder traversal, and for each node, I did a preorder traversal to get the serialization. So for n nodes, I did n traversals, hence n^2 time. As I can have a current callstack of n, and each callstack can contain a serialization of length n, the space is also n^2.

Instead of reserializing each node entirely, we could bubble up the serializations from the left and right child to a parent node, forming a unique serialization. However this is still an n operation as we are adding strings.
*/

var findDuplicateSubtrees = function (root) {
  const seenSubtrees = {}; // contains a mapping of a serialized subtree to how many times they have occured

  const result = []; // any time we see a copy of a serialized tree, and it hasn't been taken yet, add a node to the result

  function dfs(node) {
    // console.log(`dfs on: ${node} called`);
    // we have nothing to serialize if there is no node
    if (!node) {
      return;
    }

    const serializedSubtree = serializeTree(node);

    // if we already have seen this type of subtree, add it to the result
    if (serializedSubtree in seenSubtrees) {
      if (seenSubtrees[serializedSubtree] === 1) {
        result.push(node);
      }
      seenSubtrees[serializedSubtree]++;
    }
    // if we haven't seen this type of subtree, add it to what we have seen
    else {
      seenSubtrees[serializedSubtree] = 1;
    }

    dfs(node.left);
    dfs(node.right);
  }

  dfs(root);

  return result;
};

function serializeTree(root) {
  const inorder = [];
  function dfs(node) {
    if (!node) {
      inorder.push(null);
      return;
    }

    inorder.push(node.val);
    dfs(node.left);
    dfs(node.right);
  }

  dfs(root);
  return JSON.stringify(inorder);
}

// Solution 2, O(n) time and O(n) space
/*
Instead of bubbling up strings of serializations (like in the suggestion in solution 1), which would be n time as the serializations grow, we can map trees to IDs, which have fixed lengths.

A given tree has an ID, which represents a unqiue tree. Trees that look the same share an ID. We bubble up the IDs, instead of serializations, as IDs are fixed integer lengths.

We also have encodings, which are left child ID + root value + right child ID. These are sort of like serializations, and we use them to determine if we have seen a tree before. So if we have a duplicate subtree it will produce the same encoding, and we see that encoding is stored already, meaning we have a duplicate. We need to maintain a mapping of encodings to IDs, so if we do see a duplicate encoding, we can use the old ID we assigned the first time.
*/

var findDuplicateSubtrees = function (root) {
  let currentIdx = 1;

  const count = {}; // maps encodings (left id, val, right id) to how many times they have been seen

  const encodingsToIds = {}; // maps encodings to their ids, so if we see a repeat encoding we can re-use that id

  const result = [];

  function postorder(node) {
    if (!node) {
      return 0;
    }

    const leftId = postorder(node.left);
    const rightId = postorder(node.right);

    const encoding = `${leftId}|${node.val}|${rightId}`;

    // if we have never seen this encoding before, initialize it
    if (!(encoding in count)) {
      count[encoding] = 1;
      encodingsToIds[encoding] = currentIdx;
      return currentIdx++;
    }
    // if we have seen it
    else {
      // if we have seen it exactly once before, add to the result
      if (count[encoding] === 1) {
        result.push(node);
      }
      count[encoding]++;
      return encodingsToIds[encoding];
    }
  }

  postorder(root);

  return result;
};
