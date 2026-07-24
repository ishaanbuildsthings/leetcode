# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def mergeTrees(self, root1: Optional[TreeNode], root2: Optional[TreeNode]) -> Optional[TreeNode]:
        def build(a, b):
            if not a and not b:
                return None
            if not a and b:
                return b
            if a and not b:
                return a
            # a and b
            rt = TreeNode(a.val + b.val)
            left = build(a.left, b.left)
            right = build(a.right, b.right)
            rt.left = left
            rt.right = right
            return rt
        
        ans = build(root1, root2)
        return ans