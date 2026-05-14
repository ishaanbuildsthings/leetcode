# https://leetcode.com/problems/n-ary-tree-level-order-traversal/description/
# difficulty: medium
# tags: tree, bfs

# Problem
# Given an n-ary tree, return the level order traversal of its nodes' values.

# Nary-Tree input serialization is represented in their level order traversal, each group of children is separated by the null value (See examples).

# Solution O(n) time and space, standard bfs

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