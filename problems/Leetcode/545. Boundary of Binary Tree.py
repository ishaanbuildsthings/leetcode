# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def boundaryOfBinaryTree(self, root: Optional[TreeNode]) -> List[int]:
        
        res = [root.val]

        def putLeft(node):
            if not node.left and not node.right:
                return
            res.append(node.val)
            if node.left:
                putLeft(node.left)
            elif node.right:
                putLeft(node.right)
        
        if root.left:
            putLeft(root.left)

        def putLeaves(node):
            if not node.left and not node.right:
                if node != root:
                    res.append(node.val)
                return
            if node.left:
                putLeaves(node.left)
            if node.right:
                putLeaves(node.right)
        
        putLeaves(root)

        rightBoundary = []
        def putRight(node):
            if not node.left and not node.right:
                return
            rightBoundary.append(node.val)
            if node.right:
                putRight(node.right)
            elif node.left:
                putRight(node.left)
        if root.right:
            putRight(root.right)
        
        res.extend(rightBoundary[::-1])

        return res
