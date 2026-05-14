# https://leetcode.com/problems/clone-n-ary-tree/
# Difficulty: Medium
# Tags: trees

# Problem
# Given a root of an N-ary tree, return a deep copy (clone) of the tree.

# Each node in the n-ary tree contains a val (int) and a list (List[Node]) of its children.

# class Node {
#     public int val;
#     public List<Node> children;
# }
# Nary-Tree input serialization is represented in their level order traversal, each group of children is separated by the null value (See examples).

# Solution, O(n) time and O(h) space, just create a copy and dfs

"""
# Definition for a Node.
class Node:
    def __init__(self, val=None, children=None):
        self.val = val
        self.children = children if children is not None else []
"""

class Solution:
    def cloneTree(self, root: 'Node') -> 'Node':
        if not root:
            return None
        cloneRoot = Node(root.val)
        for child in root.children:
            cloneRoot.children.append(self.cloneTree(child))
        return cloneRoot