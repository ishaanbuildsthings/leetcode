# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def closestValue(self, root: Optional[TreeNode], target: float) -> int:
        resDist = inf
        res = inf
        curr = root
        while curr:
            d = abs(curr.val - target)
            if d < resDist or (d == resDist and curr.val < res):
                resDist = d
                res = curr.val
            if curr.val > target:
                curr = curr.left
            else:
                curr = curr.right
                

        
        return res
            