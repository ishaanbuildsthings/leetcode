# https://leetcode.com/problems/winner-of-the-linked-list-game/description/?envType=weekly-question&envId=2024-03-01
# difficulty: easy
# tags: linked list

# Solution
# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
class Solution:
    def gameResult(self, head: Optional[ListNode]) -> str:
        evenSurplus = 0
        curr = head
        while curr:
            evenSurplus += 1 if curr.val > curr.next.val else -1
            curr = curr.next.next
        return 'Even' if evenSurplus > 0 else 'Odd' if evenSurplus < 0 else 'Tie'
