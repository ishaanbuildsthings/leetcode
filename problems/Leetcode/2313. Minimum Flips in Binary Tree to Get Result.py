# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def minimumFlips(self, root: Optional[TreeNode], result: bool) -> int:
        @cache
        def dp(node, desired):
            if not node:
                return 0
            if not node.left and not node.right:
                return 1 - (node.val == desired)
            left1, left0, right1, right0 = dp(node.left,1), dp(node.left,0), dp(node.right,1), dp(node.right,0)
            if node.val==2:
                return min(left1,right1) if desired else left0+right0
            if node.val==3:
                return left1+right1 if desired else min(left0,right0)
            if node.val==4:
                if desired:
                    return min(left1 + right0, left0 + right1)
                return min(left0+right0,left1+right1)
            return dp(node.left if node.left else node.right, 1-desired)
                
        return dp(root, 1 if result else 0)
                