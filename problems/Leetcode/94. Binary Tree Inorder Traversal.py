# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def inorderTraversal(self, root: Optional[TreeNode]) -> List[int]:
        # res = []
        # def inorder(node):
        #     if not node: return
        #     inorder(node.left)
        #     res.append(node.val)
        #     inorder(node.right)
        # inorder(root)
        # return res

        # ITERATIVE
        res = []
        callstack = [root]
        while callstack:
            popped = callstack.pop()
            if popped.left:
                callstack.append(popped.left)
            res.append(popped.val)
            if popped.right:
                callstack.append(popped.right)
        return res
            
