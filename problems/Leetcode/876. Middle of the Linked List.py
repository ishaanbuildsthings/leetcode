# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
class Solution:
    def middleNode(self, head: Optional[ListNode]) -> Optional[ListNode]:
        slow = head
        fast = head
        # keep going if fast pointer is not the last node, or not null

        while fast and fast.next:
            slow = slow.next
            fast = fast.next.next
        
        return slow