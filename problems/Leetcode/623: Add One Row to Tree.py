# https://leetcode.com/problems/add-one-row-to-tree/description/?envType=daily-question&envId=2024-04-16
# difficulty: medium
# tags: tree

# Solution n time height space

# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def addOneRow(self, root: Optional[TreeNode], val: int, depth: int) -> Optional[TreeNode]:
        if depth == 1:
            newRoot = TreeNode(val)
            newRoot.left = root
            return newRoot

        def dfs(node, currDepth):
            if not node: return
            if currDepth == depth: return

            if currDepth == depth - 1:
                newChildLeft = TreeNode(val)
                newChildRight = TreeNode(val)

                leftTemp = node.left
                rightTemp = node.right

                newChildLeft.left = leftTemp
                newChildRight.right = rightTemp

                node.left = newChildLeft
                node.right = newChildRight
                return

            dfs(node.left, currDepth + 1)
            dfs(node.right, currDepth + 1)
        dfs(root, 1)
        return root
