# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def flipMatchVoyage(self, root: Optional[TreeNode], voyage: List[int]) -> List[int]:
        res = [] # nodes that we flip

        i = 0

        polluted = False

        def dfs(node):
            nonlocal polluted
            nonlocal i
            if voyage[i] != node.val:
                polluted = True
                return
            
            # no children
            if not node.left and not node.right:
                return
            
            # one child
            if node.left and not node.right:
                i += 1
                dfs(node.left)
                return
            
            if node.right and not node.left:
                i += 1
                dfs(node.right)
                return

            # two children
            if node.left.val == voyage[i + 1]:
                i += 1
                dfs(node.left)
                i += 1
                dfs(node.right)
            else:
                res.append(node.val)
                i += 1
                dfs(node.right)
                i += 1
                dfs(node.left)
        
        dfs(root)

        if polluted:
            return [-1]
        
        return res











