# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def hasPathSum(self, root: Optional[TreeNode], targetSum: int) -> bool:
        return ((self.hasPathSum(root.left, targetSum - root.val) or 
        self.hasPathSum(root.right, targetSum - root.val))
        if root and (root.left or root.right) else targetSum == root.val if root else False)