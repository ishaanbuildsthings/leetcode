# https://leetcode.com/problems/linked-list-frequency/description/
# difficulty: easy
# tags: linked list

# Solution
# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
class Solution:
    def frequenciesOfElements(self, head: Optional[ListNode]) -> Optional[ListNode]:
        frqs = defaultdict(int)
        curr = head
        while curr:
            frqs[curr.val] += 1
            curr = curr.next

        resHead = ListNode(None)
        curr = resHead
        for key in frqs:
            curr.next = ListNode(frqs[key])
            curr = curr.next
        return resHead.next