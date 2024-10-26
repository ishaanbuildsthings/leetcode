# https://leetcode.com/problems/remove-nodes-from-linked-list/?envType=daily-question&envId=2024-05-06
# difficulty: medium
# tags: linked list, recursion

# Solution, O(n) time and space, kind of a bad solution, could use basic recursion or a hashmap with reverse pointers

# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
class Solution:
    def removeNodes(self, head: Optional[ListNode]) -> Optional[ListNode]:
        dummy = ListNode(None)
        dummy.next = head

        @cache
        def biggestToRight(node):
            if not node or not node.next:
                return float('-inf')
            # base case
            if not node.next.next:
                return node.next.val

            return max(node.next.val, biggestToRight(node.next))

        curr = dummy
        while curr and curr.next:
            if biggestToRight(curr.next) > curr.next.val:
                curr.next = curr.next.next
            else:
                curr = curr.next

        return dummy.next
