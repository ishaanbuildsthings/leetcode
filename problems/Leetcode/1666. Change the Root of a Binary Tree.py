"""
# Definition for a Node.
class Node:
    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None
        self.parent = None
"""

class Solution:
    def flipBinaryTree(self, root: 'Node', leaf: 'Node') -> 'Node':
        prev = None
        curr = leaf

        while curr != root:
            parent = curr.parent
            isLeft = parent.left is curr
            isRight = not isLeft
        
            if curr.left is not None:
                curr.right = curr.left
            
            curr.left = parent

            if isLeft:
                parent.left = None
            else:
                parent.right = None
            
            curr.parent = prev
            prev = curr
            curr = parent
        
        curr.parent = prev
        return leaf

