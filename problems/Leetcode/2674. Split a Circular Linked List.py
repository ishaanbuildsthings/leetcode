# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
class Solution:
    def splitCircularLinkedList(self, list: Optional[ListNode]) -> List[Optional[ListNode]]:
        n = 1
        first = list
        curr = list
        while curr:
            nxt = curr.next
            if nxt == first:
                break
            n += 1
            curr = nxt
        
        firstHalf = math.ceil(n / 2)

        v0 = list
        v1 = None
        currSeen = 0
        curr = list
        while currSeen < n:
            currSeen += 1
            if currSeen == firstHalf:
                grab = curr.next
                curr.next = v0
                curr = grab
                continue
            if currSeen != n:
                curr = curr.next
        
        curr.next = grab
        
        return [list, grab]