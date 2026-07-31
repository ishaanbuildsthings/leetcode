# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
class Solution:
    def deleteNodes(self, head: ListNode, m: int, n: int) -> ListNode:
        d = ListNode()
        d.next = head

        turn = 0 # 0 means we are keeping
        count = 0 # nodes kept or deleted
        curr = d
        while curr and curr.next:
            if turn == 0:
                curr = curr.next
                count += 1
                if count == m:
                    turn ^= 1
                    count = 0
            elif turn == 1:
                curr.next = curr.next.next
                count += 1
                if count == n:
                    turn ^= 1
                    count = 0
        
        return d.next
