# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def increasingBST(self, root: TreeNode) -> TreeNode:
        res = []
        def preorder(node):
            if not node:
                return
            preorder(node.left)
            res.append(node)
            preorder(node.right)
        preorder(root)
        root = res[0]
        for idx in range(1, len(res)):
            prev = res[idx - 1]
            prev.right = res[idx]
            prev.left = None
        res[-1].left = None
        res[-1].right = None
        return res[0]