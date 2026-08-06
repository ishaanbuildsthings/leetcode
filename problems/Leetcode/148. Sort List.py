# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
class Solution:
    def sortList(self, head: Optional[ListNode]) -> Optional[ListNode]:
        if not head:
            return None

        def merge(a, b):
            p1, p2 = a, b
            d = ListNode()
            curr = d
            while p1 and p2:
                if p1.val <= p2.val:
                    curr.next = p1
                    p1 = p1.next
                else:
                    curr.next = p2
                    p2 = p2.next
                curr = curr.next
            
            while p1:
                curr.next = p1
                curr = curr.next
                p1 = p1.next
            while p2:
                curr.next = p2
                curr = curr.next
                p2 = p2.next
            return d.next
        
        def mySort(ll):
            if not ll.next:
                return ll
            size = 0
            c = ll
            while c:
                size += 1
                c = c.next
            head = ll
            prev = None
            for _ in range(size // 2):
                prev = head
                head = head.next
            second = prev.next
            prev.next = None
            sortLeft = mySort(ll)
            sortRight = mySort(second)
            merged = merge(sortLeft, sortRight)
            return merged
        
        return mySort(head)