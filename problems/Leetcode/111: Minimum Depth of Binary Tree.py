# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def minDepth(self, root: Optional[TreeNode]) -> int:
        if not root: return 0
        def dfs(node):
            if not node.left and not node.right:
                return 0
            return 1 + min(dfs(node.left) if node.left else inf, dfs(node.right) if node.right else inf)
        return dfs(root) + 1