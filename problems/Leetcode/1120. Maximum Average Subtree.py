# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def maximumAverageSubtree(self, root: Optional[TreeNode]) -> float:
        res = 0
        
        def dfs(node):
            nonlocal res

            # base case
            if not node.left and not node.right:
                res = max(res, node.val)
                return [1, node.val] # size and weight
            
            totalSize = 1
            totalWeight = node.val

            if node.left:
                lSize, lWeight = dfs(node.left)
                totalSize += lSize
                totalWeight += lWeight
            if node.right:
                rSize, rWeight = dfs(node.right)
                totalSize += rSize
                totalWeight += rWeight
            
            finalAvg = totalWeight / totalSize
            res = max(res, finalAvg)
            return [totalSize, totalWeight]
        
        dfs(root)
        return res