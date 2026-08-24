# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def subtreeWithAllDeepest(self, root: TreeNode) -> TreeNode:
        # can probably do in one function
        
        numDeepest = 0
        deepest = -1

        def dfs(node, depth):
            nonlocal deepest
            nonlocal numDeepest

            if not node:
                return
            if depth > deepest:
                deepest = depth
                numDeepest = 1
            elif depth == deepest:
                numDeepest += 1
            
            dfs(node.left, depth + 1)
            dfs(node.right, depth + 1)
        
        dfs(root, 0)
        
        res = None
        breakFlag = False

        def dfs(node, depth):
            nonlocal res
            nonlocal breakFlag

            if not node:
                return 0
            if depth == deepest:
                if numDeepest == 1:
                    res = node
                    breakFlag = True
                    return
                return 1
            leftCount = dfs(node.left, depth + 1)
            if breakFlag:
                return
            rightCount = dfs(node.right, depth + 1)
            if breakFlag:
                return
            if leftCount + rightCount == numDeepest:
                res = node
                breakFlag = True
                return
            return leftCount + rightCount
        
        dfs(root, 0)

        return res

            