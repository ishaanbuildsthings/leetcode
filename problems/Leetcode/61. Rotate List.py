# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
class Solution:
    def rotateRight(self, head: Optional[ListNode], k: int) -> Optional[ListNode]:
        if not head:
            return None

        size = 0
        tail = head
        last = None
        while tail:
            size += 1
            last = tail
            tail = tail.next
        
        if size == 1:
            return head
        if k % size == 0:
            return head
        
        k %= size

        # we need access to before the kth last one
        prev = head
        for _ in range(size - k - 1):
            prev = prev.next
        
        right = prev.next
        prev.next = None

        last.next = head

        return right
        