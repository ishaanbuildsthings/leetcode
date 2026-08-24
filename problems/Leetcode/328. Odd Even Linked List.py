# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
class Solution:
    def oddEvenList(self, head: Optional[ListNode]) -> Optional[ListNode]:
        oddHead = ListNode()
        evenHead = ListNode()
        finalOdd = oddHead
        finalEven = evenHead

        ops = 1
        curr = head
        while curr:
            if ops % 2:
                oddHead.next = curr
                oddHead = curr
            else:
                evenHead.next = curr
                evenHead = curr
            ops += 1
            curr = curr.next

        evenHead.next = None
        oddHead.next = None

        res = ListNode()
        ret = res
        curr = finalOdd.next
        while curr:
            res.next = curr
            curr = curr.next
            res = res.next
        curr = finalEven.next
        while curr:
            res.next = curr
            res = res.next
            curr = curr.next
        return ret.next