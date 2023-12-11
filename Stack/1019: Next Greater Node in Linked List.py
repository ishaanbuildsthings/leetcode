# https://leetcode.com/problems/next-greater-node-in-linked-list/description/
# difficulty: medium
# tags: stack, linked list, great question

# Problem
# You are given the head of a linked list with n nodes.

# For each node in the list, find the value of the next greater node. That is, for each node, find the value of the first node that is next to it and has a strictly larger value than it.

# Return an integer array answer where answer[i] is the value of the next greater node of the ith node (1-indexed). If the ith node does not have a next greater node, set answer[i] = 0.

# Solution, O(n) time and space, standard stack

# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
class Solution:
    def nextLargerNodes(self, head: Optional[ListNode]) -> List[int]:
        resMap = {}
        stack = [] # holds [node, index]
        curr = head
        i = 0
        while curr:
            n = i
            while stack and curr.val > stack[-1][0].val:
                node, index = stack.pop()
                resMap[index] = curr.val
            stack.append([curr, i])
            i += 1
            curr = curr.next

        return [
            resMap[i] if i in resMap else 0
            for i in range(n + 1)
        ]
