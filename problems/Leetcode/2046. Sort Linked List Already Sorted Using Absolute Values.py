# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
class Solution:
    def sortLinkedList(self, head: Optional[ListNode]) -> Optional[ListNode]:
        dNeg = ListNode()
        dPos = ListNode()
        neg = dNeg
        pos = dPos
        curr = head
        while curr:
            if curr.val >= 0:
                pos.next = curr
                pos = pos.next
            else:
                neg.next = curr
                neg = neg.next
            curr = curr.next
        
        pos.next = None
        neg.next = None

        # now reverse negatives
        prev = None
        curr = dNeg.next
        while curr:
            nxt = curr.next
            curr.next = prev
            prev = curr
            curr = nxt
        

        dummy = ListNode()
        head = dummy
        neg = prev
        pos = dPos.next
        while neg:
            head.next = neg
            neg = neg.next
            head = head.next
        while pos:
            head.next = pos
            pos = pos.next
            head = head.next
        
        return dummy.next
