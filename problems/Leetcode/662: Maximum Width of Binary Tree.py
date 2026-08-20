# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def widthOfBinaryTree(self, root: Optional[TreeNode]) -> int:
        res = 0
        rowMn = defaultdict(lambda : inf)
        rowMx = defaultdict(lambda : -inf)

        def dfs(node, idx, row):
            rowMn[row] = min(rowMn[row], idx)
            rowMx[row] = max(rowMx[row], idx)
            if node.left:
                dfs(node.left, 2 * idx, row + 1)
            if node.right:
                dfs(node.right, 2 * idx + 1, row + 1)
        dfs(root, 1, 0)
        for key in rowMn:
            res = max(res, rowMx[key] - rowMn[key])
        return res + 1