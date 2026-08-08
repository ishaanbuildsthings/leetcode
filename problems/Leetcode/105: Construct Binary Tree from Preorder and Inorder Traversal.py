# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def buildTree(self, preorder: List[int], inorder: List[int]) -> Optional[TreeNode]:
        def construct(pl, pr, il, ir):
            if pl > pr:
                return None
            root = TreeNode(preorder[pl])
            # find the index of the root inside the inorder
            rootI = inorder.index(preorder[pl])

            # construct the left half
            newIl = il
            newIr = rootI - 1
            width = newIr - newIl + 1
            newPl = pl + 1
            newPr = newPl + width - 1

            left = construct(newPl, newPr, newIl, newIr)

            # construct the right half
            newIl = rootI + 1
            newIr = ir
            width = newIr - newIl + 1
            newPr = pr
            newPl = newPr - width + 1

            right = construct(newPl, newPr, newIl, newIr)

            root.left = left
            root.right = right
            return root
        
        return construct(0, len(preorder) - 1, 0, len(inorder) - 1)