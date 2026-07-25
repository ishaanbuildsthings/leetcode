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
 * @param {number} k
 * @return {boolean}
 */
var findTarget = function(root, k) {
    const numSet = new Set();

    function dfs(node) {
        if (!node) {
            return;
        }
        numSet.add(node.val);
        dfs(node.left);
        dfs(node.right);
    }

    dfs(root);

    for (const num of Array.from(numSet)) {
        if (numSet.has(k - num) && k !== 2 * num) { // no duplicate values in BSTs, so we can't reuse a number twice
            return true;
        }
    }
    
    return false;
};