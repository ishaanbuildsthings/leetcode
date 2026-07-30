# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
class Solution:
    def getDecimalValue(self, head: ListNode) -> int:
        res = 0
        curr = head
        while curr:
            res *= 2
            if curr.val:
                res += 1
            curr = curr.next
        return res
