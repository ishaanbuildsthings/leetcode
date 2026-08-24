# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
class Solution:
    def plusOne(self, head: ListNode) -> ListNode:
        prevs = {}
        curr = head
        while curr and curr.next:
            prevs[curr.next] = curr
            curr = curr.next
        prevs[head] = None
        
        carry = 1
        while carry:
            if curr is None:
                newHead = ListNode(1)
                newHead.next = head
                return newHead
            newVal = curr.val + carry
            if newVal == 10:
                carry = 1
                curr.val = 0
                curr = prevs[curr]
                continue
            curr.val = curr.val + 1
            carry = 0
        
        return head