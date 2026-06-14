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
 * @param {number} targetSum
 * @return {number}
 */
var pathSum = function(root, targetSum) {
    const prefixes = {}; // maps a prefix sum to the amount of times we have that prefix, to know how many times we can cut off a certain prefix to get the sum
    
    let result = 0;
    
    function dfs(node, runningSum) {
        if (!node) {
            return;
        }
                
        const newSum = runningSum + node.val;
        
                
        // if we reached the sum precisely, we can add a result
        if (newSum === targetSum) {
            result++;
        }
        
        // if we can chop off a needed prefix, we can add a result
        const prefixToChopOff = newSum - targetSum;
        if (prefixToChopOff in prefixes) {
            result += prefixes[prefixToChopOff]; // for every occurence, we could create a different path
        }
        
        if (newSum in prefixes) {
            prefixes[newSum]++;
        } else {
            prefixes[newSum] = 1;
        }
        
        dfs(node.left, newSum);
        dfs(node.right, newSum);
        
        // before bubbling back up, we need to remove the prefix we formed
        prefixes[newSum]--;
        
        
    }
    
    dfs(root, 0);
    
    return result;
};