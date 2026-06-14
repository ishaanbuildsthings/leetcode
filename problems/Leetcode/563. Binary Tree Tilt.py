# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def findTilt(self, root: Optional[TreeNode]) -> int:
        res = 0
        def dfs(node):
            nonlocal res

            # base case
            if not node:
                return 0 # returns sum
            
            leftSum = dfs(node.left)
            rightSum = dfs(node.right)
            diff = abs(leftSum - rightSum)
            res += diff
            return leftSum + rightSum + node.val
        
        dfs(root)
        return res