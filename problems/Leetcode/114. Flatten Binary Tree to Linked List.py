# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def flatten(self, root: Optional[TreeNode]) -> None:
        """
        Do not return anything, modify root in-place instead.
        """
        dummy = TreeNode()
        dummy.right = root
        prev = dummy
        def preorder(node):
            nonlocal prev
            if not node:
                return
            left, right = node.left, node.right
            prev.right = node
            prev.left = None
            prev = node
            if left:
                preorder(left)
            if right:
                preorder(right)
        preorder(root)
        return dummy.right
        