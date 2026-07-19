# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def countDominantNodes(self, root: TreeNode | None) -> int:
        res = 0
        def dfs(node):
            nonlocal res
            if not node:
                return -inf
            mx = node.val
            for child in [node.left, node.right]:
                mx = max(mx, dfs(child))
            if mx == node.val:
                res += 1
            return mx

        dfs(root)

        return res