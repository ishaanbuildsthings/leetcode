"""
# Definition for a Node.
class Node:
    def __init__(self, x: int, next: 'Node' = None, random: 'Node' = None):
        self.val = int(x)
        self.next = next
        self.random = random
"""

class Solution:
    def copyRandomList(self, head: 'Optional[Node]') -> 'Optional[Node]':
        if not head:
            return None
            
        oldToNew = {}

        # populate the oldToNew map, create the new nodes but don't assign pointers yet
        curr = head
        while curr:
            newCopy = Node(curr.val)
            oldToNew[curr] = newCopy
            curr = curr.next
        
        oldCurr = head
        while oldCurr:
            newCurr = oldToNew[oldCurr]
            newNext = oldToNew[oldCurr.next] if oldCurr.next else None
            newRandom = oldToNew[oldCurr.random] if oldCurr.random else None
            newCurr.next = newNext
            newCurr.random = newRandom
            oldCurr = oldCurr.next

        return oldToNew[head]