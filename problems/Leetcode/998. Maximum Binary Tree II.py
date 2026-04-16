# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def insertIntoMaxTree(self, root: Optional[TreeNode], val: int) -> Optional[TreeNode]:
        
        def constructArr(node):
            if not node:
                return []
            return constructArr(node.left) + [node.val] + constructArr(node.right)

        arr = constructArr(root)
        arr.append(val)
        
        def constructTree(l, r):
            if l > r:
                return None
            mx = max(arr[l:r+1])
            mxI = arr.index(mx)
            rt = TreeNode(mx)
            leftTree = constructTree(l, mxI - 1)
            rightTree = constructTree(mxI + 1, r)
            rt.left = leftTree
            rt.right = rightTree
            return rt
        
        return constructTree(0, len(arr) - 1)