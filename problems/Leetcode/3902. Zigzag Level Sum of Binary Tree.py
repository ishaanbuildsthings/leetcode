# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def zigzagLevelSum(self, root: TreeNode | None) -> list[int]:
        if not root:
            return []
        layer = [root]
        level = 1
        res = []
        while layer:
            score = 0
            fail = False
            length = len(layer)
            iter = layer[::-1]
            nlayer = []
            for node in iter:
                if not (node.left if level % 2 else node.right):
                    fail = True
                if not fail:
                    score += node.val
                if level % 2:
                    if node.left:
                        nlayer.append(node.left)
                    if node.right:
                        nlayer.append(node.right)
                else:
                    if node.right:
                        nlayer.append(node.right)
                    if node.left:
                        nlayer.append(node.left)
            layer = nlayer
            res.append(score)
            level += 1
        
        return res
        