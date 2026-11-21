# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
class Solution:
    def removeNodes(self, head: Optional[ListNode]) -> Optional[ListNode]:
        
        def rec(node):
            if not node:
                return None, -inf
            headRight, mxRight = rec(node.next)
            if mxRight > node.val:
                return headRight, mxRight
            node.next = headRight
            return node, node.val
        
        return rec(head)[0]
            