# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def btreeGameWinningMove(self, root: Optional[TreeNode], n: int, x: int) -> bool:
        
        @cache
        def sz(node):
            if not node:
                return 0
            return 1 + sz(node.left) + sz(node.right)
        

        def findX(node):
            if not node:
                return None
            if node.val == x:
                return node
            return findX(node.left) or findX(node.right)
        
        xNode = findX(root)


        xLeftSz = sz(xNode.left)
        xRightSz = sz(xNode.right)
        totalSz = sz(root)
        if xLeftSz > (totalSz - xLeftSz):
            return True
        if xRightSz > (totalSz - xRightSz):
            return True
        if xNode != root:
            xSz = sz(xNode)
            totalSize = sz(root)
            aboveSz = totalSize - xSz
            if aboveSz > (totalSize / 2):
                return True
        
        return False
        