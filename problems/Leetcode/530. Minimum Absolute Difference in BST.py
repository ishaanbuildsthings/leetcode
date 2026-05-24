# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def getMinimumDifference(self, root: Optional[TreeNode]) -> int:
        p = -inf
        ans = inf
        def inorder(node):
            nonlocal p
            nonlocal ans
            if not node:
                return
            inorder(node.left)
            diff = abs(p - node.val)
            ans = min(ans, diff)
            p = node.val
            inorder(node.right)
        inorder(root)
        return ans

            
            