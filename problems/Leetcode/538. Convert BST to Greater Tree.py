# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def convertBST(self, root: Optional[TreeNode]) -> Optional[TreeNode]:
        # # a node needs to add anything in the right subtree
        # # and add anything from above it
        # def dfs(node, sumFromAbove):
        #     if not node:
        #         return 0
        #     rightSum = dfs(node.right, sumFromAbove) # this line is confusing
        #     addingToLeft = sumFromAbove + node.val + rightSum
        #     orig = node.val
        #     node.val += sumFromAbove + rightSum
        #     leftSum = dfs(node.left, addingToLeft)
        #     return leftSum + rightSum + orig
        # dfs(root, 0)

        # return root

        runningSum = 0
        def revInorder(node):
            nonlocal runningSum
            if not node:
                return
            revInorder(node.right)
            newVal = node.val + runningSum
            runningSum += node.val
            node.val = newVal
            revInorder(node.left)
        revInorder(root)
        return root