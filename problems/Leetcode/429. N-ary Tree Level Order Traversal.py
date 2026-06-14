"""
# Definition for a Node.
class Node:
    def __init__(self, val=None, children=None):
        self.val = val
        self.children = children
"""

class Solution:
    def levelOrder(self, root: 'Node') -> List[List[int]]:
        if not root:
            return []

        q = collections.deque()
        q.append(root)
        res = []
        while q:
            length = len(q)
            level = []
            for _ in range(length):
                popped = q.popleft()
                for child in popped.children:
                    q.append(child)
                level.append(popped)
            res.append(level)

        return [
            [node.val for node in level]
            for level in res
        ]