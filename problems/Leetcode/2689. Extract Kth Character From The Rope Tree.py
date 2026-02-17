# Definition for a rope tree node.
# class RopeTreeNode(object):
#     def __init__(self, len=0, val="", left=None, right=None):
#         self.len = len
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def getKthCharacter(self, root: Optional[object], k: int) -> str:
        """
        :type root: Optional[RopeTreeNode]
        """
        if root.val:
            return root.val[k - 1]
        if root.left and not root.right:
            return self.getKthCharacter(root.left, k)
        if root.right and not root.left:
            return self.getKthCharacter(root.right, k)
        
        # have both

        # left is a string and we want it
        if root.left.val and len(root.left.val) >= k:
            return self.getKthCharacter(root.left, k)
        # left is a number and we want it
        if root.left.len and root.left.len >= k:
            return self.getKthCharacter(root.left, k)
        
        leftLength = len(root.left.val) if root.left.val else root.left.len

        return self.getKthCharacter(root.right, k - leftLength)

        