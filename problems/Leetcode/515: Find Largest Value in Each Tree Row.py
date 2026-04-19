# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def largestValues(self, root: Optional[TreeNode]) -> List[int]:
        # edge case
        if not root:
            return []

        res = []
        q = collections.deque()
        q.append(root)

        while q:
            length = len(q)
            maxForLayer = float('-inf')
            for _ in range(length):
                node = q.popleft()
                maxForLayer = max(maxForLayer, node.val)
                if node.left:
                    q.append(node.left)
                if node.right:
                    q.append(node.right)
            res.append(maxForLayer)
        
        return res