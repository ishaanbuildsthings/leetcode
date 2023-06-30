class Node {
  constructor(val) {
    this.left = null;
    this.right = null;
    this.val = val;
  }
}

const rootNode = new Node(5);
const leftNode = new Node(2);
const rightNode = new Node(10);

rootNode.left = leftNode;
rootNode.right = rightNode;
/*

       5
     /   \
    2    10

    2->5->10

    8
   / \
  5
*/

var minDiffInBST = function (root) {
  let minDifference = Infinity;
  let prev = null;
  function inorder(node) {
    if (!node) {
      return;
    }

    if (node.left) {
      prev = inorder(node.left);
      const currentDifference = node.val - prev.val;
      minDifference = Math.min(minDifference, currentDifference);
    }

    prev = node.val;
    inorder(node.right);

    return node;
  }

  inorder(root);

  return minDifference;
};

console.log(minDiffInBST(rootNode));
