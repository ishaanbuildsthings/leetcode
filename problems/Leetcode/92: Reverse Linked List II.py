# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
class Solution:
    def reverseBetween(self, head: Optional[ListNode], left: int, right: int) -> Optional[ListNode]:
        d = ListNode()
        d.next = head
        def rev(L, R):
            l = L.next
            prev = None
            curr = L.next
            while curr is not R:
                nxt = curr.next
                curr.next = prev
                prev = curr
                curr = nxt
            L.next = prev
            l.next = R
        
        pos = 1
        prev = d
        curr = head
        while pos != left:
            prev = curr
            curr = curr.next
            pos += 1
        while pos != right:
            curr = curr.next
            pos += 1
                
        rev(prev, curr.next)
        return d.next
