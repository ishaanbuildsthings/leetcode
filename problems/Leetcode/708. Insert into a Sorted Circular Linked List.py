"""
# Definition for a Node.
class Node:
    def __init__(self, val=None, next=None):
        self.val = val
        self.next = next
"""

class Solution:
    def insert(self, head: 'Optional[Node]', insertVal: int) -> 'Node':
        if not head:
            node = Node(insertVal)
            node.next = node
            return node
        
        curr = head
        while True:
            # if we fit between 2 nodes put there
            if curr.val <= insertVal <= curr.next.val:
                break
            # if we are at a max->min point and we fit there put it
            if curr.val > curr.next.val and (insertVal >= curr.val or insertVal <= curr.next.val):
                break
            # tricky case everything in the same
            curr = curr.next
            if curr == head:
                break
        curr.next = Node(insertVal, curr.next)
        return head