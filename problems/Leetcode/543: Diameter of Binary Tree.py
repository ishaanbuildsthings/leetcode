# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def diameterOfBinaryTree(self, root: Optional[TreeNode]) -> int:
        res = 0
        
        def dfs(node):
            nonlocal res

            # base
            if not node:
                return 0
            
            leftLength = dfs(node.left)
            rightLength = dfs(node.right)
            longestLength = 1 + max(leftLength, rightLength)
            res = max(res, leftLength + rightLength + 1)

            return longestLength
        
        dfs(root)

        return res - 1