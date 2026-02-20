# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def printTree(self, root: Optional[TreeNode]) -> List[List[str]]:
        def findDepth(node):
            if not node:
                return 0
            return 1 + max(findDepth(node.left), findDepth(node.right))
        depth = findDepth(root)

        width = 2**(depth) - 1
        res = [
            ['' for _ in range(width)] for _ in range(depth)
        ]

        def dfs(node, r, c):
            if not node:
                return
            res[r][c] = str(node.val)

            leftCol = c - 2**((depth-1) - r - 1)
            rightCol = c + 2**((depth-1) - r - 1)
            dfs(node.left, r + 1, leftCol)
            dfs(node.right, r + 1, rightCol)
        
        dfs(root, 0, width // 2)

        return res

