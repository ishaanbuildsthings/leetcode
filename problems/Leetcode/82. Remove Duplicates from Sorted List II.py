# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
class Solution:
    def deleteDuplicates(self, head: Optional[ListNode]) -> Optional[ListNode]:
        d = ListNode()
        d.next = head

        prev = d
        curr = head
        # curr is always the head of a new number type
        while curr:
            if curr.next and curr.val != curr.next.val:
                prev = curr
                curr = curr.next
                continue
            if not curr.next:
                return d.next

            # find the last tail that equals curr
            tail = curr.next
            while tail and tail.val == curr.val:
                tail = tail.next
            
            prev.next = tail
            curr = tail
        
        return d.next