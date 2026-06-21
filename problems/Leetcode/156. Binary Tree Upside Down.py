# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def upsideDownBinaryTree(self, root: Optional[TreeNode]) -> Optional[TreeNode]:
        if not root:
            return None
        
        final = root
        while final.left:
            final = final.left
        
        def rec(node):
            if not node.left:
                return node
            left = rec(node.left)
            right = node.right
            left.right = node
            left.left = right
            return node
        
        rec(root)
        root.left = root.right = None
        
        return final