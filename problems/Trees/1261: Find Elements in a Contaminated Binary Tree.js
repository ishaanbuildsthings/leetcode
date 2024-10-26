// https://leetcode.com/problems/find-elements-in-a-contaminated-binary-tree/description/
// difficulty: Medium
// tags: binary tree

// Problem
/*
Given a binary tree with the following rules:

root.val == 0
If treeNode.val == x and treeNode.left != null, then treeNode.left.val == 2 * x + 1
If treeNode.val == x and treeNode.right != null, then treeNode.right.val == 2 * x + 2
Now the binary tree is contaminated, which means all treeNode.val have been changed to -1.

Implement the FindElements class:

FindElements(TreeNode* root) Initializes the object with a contaminated binary tree and recovers it.
bool find(int target) Returns true if the target value exists in the recovered binary tree.
*/

// Solution, O(n) time/space for construct, O(1) find
/*
Recovering the numbers is simple, just start at the root and call a basic recursive function. I also just added all the seen numbers for O(1) find, since we are storing O(n) space in the tree anyway I figured the size is not a big deal. (10^4 values per constraints as well). There is probably some log n find solution using math / bits but I didn't spend time thinking about it.
*/

/**
 * Definition for a binary tree node.
 * function TreeNode(val, left, right) {
 *     this.val = (val===undefined ? 0 : val)
 *     this.left = (left===undefined ? null : left)
 *     this.right = (right===undefined ? null : right)
 * }
 */
/**
 * @param {TreeNode} root
 */
var FindElements = function (root) {
  this.numSet = new Set();

  // arrow function for lexical this
  const assignAndRecurse = (node) => {
    this.numSet.add(node.val);

    if (node.left) {
      node.left.val = 2 * node.val + 1;
      assignAndRecurse(node.left);
    }

    if (node.right) {
      node.right.val = 2 * node.val + 2;
      assignAndRecurse(node.right);
    }
  };

  root.val = 0;
  assignAndRecurse(root);

  this.root = root;
};

/**
 * @param {number} target
 * @return {boolean}
 */
FindElements.prototype.find = function (target) {
  return this.numSet.has(target);
};

/**
 * Your FindElements object will be instantiated and called as such:
 * var obj = new FindElements(root)
 * var param_1 = obj.find(target)
 */
