# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
class Solution:
    def insertionSortList(self, head: Optional[ListNode]) -> Optional[ListNode]:
        d = ListNode()
        currInsert = head
        while currInsert:
            nextNode = currInsert.next
            currInsert.next = None

            # insert it

            # insert at beginning
            if not d.next:
                d.next = currInsert
                currInsert = nextNode
                continue
            
            follow = d.next
            prev = d
            while follow:
                if follow.val >= currInsert.val:
                    prev.next = currInsert
                    currInsert.next = follow
                    break
                prev = follow
                follow = follow.next
            
            if currInsert.val > prev.val:
                prev.next = currInsert
            
            currInsert = nextNode
        
        return d.next
            