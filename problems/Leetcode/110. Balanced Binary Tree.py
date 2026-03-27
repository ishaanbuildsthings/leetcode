# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def isBalanced(self, root: Optional[TreeNode]) -> bool:
        fail = False
        def dfs(node, depth):
            nonlocal fail
            if not node:
                return depth - 1
            d1 = dfs(node.left, depth + 1)
            d2 = dfs(node.right, depth + 1)
            if abs(d1 - d2) > 1:
                fail = True
            return max(d1, d2)
        dfs(root, 0)
        return not fail
