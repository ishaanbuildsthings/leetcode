# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def bstFromPreorder(self, preorder: List[int]) -> Optional[TreeNode]:
        if len(preorder) == 0:
            return None
        rt = TreeNode(preorder[0])
        gFound = False
        for i in range(1, len(preorder)):
            if preorder[i] > rt.val:
                rt.right = self.bstFromPreorder(preorder[i:])
                if i > 1:
                    rt.left = self.bstFromPreorder(preorder[1:i])
                gFound = True
                break
        if not gFound:
            rt.left = self.bstFromPreorder(preorder[1:])
        return rt
        