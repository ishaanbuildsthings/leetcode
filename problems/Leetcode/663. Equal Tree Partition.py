# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def checkEqualTree(self, root: Optional[TreeNode]) -> bool:
        @cache
        def treeSum(node):
            if not node.left and not node.right:
                return node.val
            resHere = node.val
            if node.left:
                resHere += treeSum(node.left)
            if node.right:
                resHere += treeSum(node.right)
            return resHere
        
        totAll = treeSum(root)
        g = False
        def find(node):
            nonlocal g
            if g:
                return
            if treeSum(node) * 2 == totAll and node != root:
                g = True
                return
            if node.left:
                find(node.left)
            if node.right:
                find(node.right)
        find(root)
        return g