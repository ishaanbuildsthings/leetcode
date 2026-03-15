"""
# Definition for a Node.
class Node:
    def __init__(self, val=None, children=None):
        self.val = val
        self.children = children if children is not None else []
"""

class Solution:
    def diameter(self, root: 'Node') -> int:
        """
        :type root: 'Node'
        :rtype: int
        """

        @cache
        def depth(node):
            if not node.children:
                return 1
            return 1 + max(depth(child) for child in node.children)
        

        # can use heapq.nlargest to speed it up, also can roll up into one function easily
        res = 0
        def dfs(node):
            nonlocal res
            depths = [depth(child) for child in node.children]
            depths.sort(reverse=True)
            if not depths:
                return
            if len(depths) == 1:
                res = max(res, depths[0])
                dfs(node.children[0])
            else:
                res = max(res, depths[0] + depths[1])
                for child in node.children:
                    dfs(child)
        
        dfs(root)

        return res