/**
 * // Definition for a Node.
 * function Node(val,children) {
 *    this.val = val;
 *    this.children = children;
 * };
 */

/**
 * @param {Node|null} root
 * @return {number}
 */
var maxDepth = function(root) {
    // base case, if we have null the height is 0
    if (!root) return 0;
    // if we have a node with no children, the height is 1, this is needed because otherwise we would return Math.max() since node.children is empty
    if (root.children.length === 0) return 1;

    // otherwise, take every child, run it through the recurse function (adding 1), and take the max of all those children
    return Math.max(...root.children.map(child => 1 + maxDepth(child)));
};