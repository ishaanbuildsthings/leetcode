"""
# Definition for a QuadTree node.
class Node:
    def __init__(self, val, isLeaf, topLeft, topRight, bottomLeft, bottomRight):
        self.val = val
        self.isLeaf = isLeaf
        self.topLeft = topLeft
        self.topRight = topRight
        self.bottomLeft = bottomLeft
        self.bottomRight = bottomRight
"""

class Solution:
    def intersect(self, qt1: 'Node', qt2: 'Node') -> 'Node':
        if qt1.isLeaf:
                if qt1.val == 1:
                    return qt1
                return qt2
        
        if qt2.isLeaf:
            if qt2.val == 1:
                return qt2
            return qt1
        
        tl = self.intersect(qt1.topLeft, qt2.topLeft)
        tr = self.intersect(qt1.topRight, qt2.topRight)
        br = self.intersect(qt1.bottomRight, qt2.bottomRight)
        bl = self.intersect(qt1.bottomLeft, qt2.bottomLeft)

        if tl.isLeaf and tr.isLeaf and br.isLeaf and bl.isLeaf and tl.val == tr.val == bl.val == br.val:
            return Node(tl.val, True)

        return Node(None, False, tl, tr, bl, br)