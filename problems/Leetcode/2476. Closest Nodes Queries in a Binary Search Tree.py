# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def closestNodes(self, root: Optional[TreeNode], queries: List[int]) -> List[List[int]]:

        vals = []
        def inorder(node):
            if not node:
                return
            inorder(node.left)
            vals.append(node.val)
            inorder(node.right)
        inorder(root)

        print(vals)
        
        def largestLteX(x):
            l = 0
            r = len(vals) - 1
            resI = None
            while l <= r:
                m = (r + l) // 2
                if vals[m] <= x:
                    resI = m
                    l = m + 1
                else:
                    r = m - 1
            return -1 if resI is None else vals[resI]
        
        def smallestGteX(x):
            l = 0
            r = len(vals) - 1
            resI = None
            while l <= r:
                m = (r + l) // 2
                if vals[m] >= x:
                    resI = m
                    r = m - 1
                else:
                    l = m + 1
            return -1 if resI is None else vals[resI]


        return [
            [
                largestLteX(q),
                smallestGteX(q)
            ] for q in queries
        ]
