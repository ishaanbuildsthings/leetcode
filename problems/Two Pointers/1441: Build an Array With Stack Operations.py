# https://leetcode.com/problems/build-an-array-with-stack-operations/description/
# difficulty: medium
# tags: two pointers

# Problem
# You are given an integer array target and an integer n.

# You have an empty stack with the two following operations:

# "Push": pushes an integer to the top of the stack.
# "Pop": removes the integer on the top of the stack.
# You also have a stream of the integers in the range [1, n].

# Use the two stack operations to make the numbers in the stack (from the bottom to the top) equal to target. You should follow the following rules:

# If the stream of the integers is not empty, pick the next integer from the stream and push it to the top of the stack.
# If the stack is not empty, pop the integer at the top of the stack.
# If, at any moment, the elements in the stack (from the bottom to the top) are equal to target, do not read new integers from the stream and do not do more operations on the stack.
# Return the stack operations needed to build target following the mentioned rules. If there are multiple valid answers, return any of them.

# Solution, O(n) time O(1) space, just standard two pointers

class Solution:
    def buildArray(self, target: List[int], n: int) -> List[str]:
        streamed = 1
        # i represents matching the number we need
        i = 0
        res = []
        while i < len(target):
            res.append('Push')
            if streamed != target[i]:
                res.append('Pop')
            else:
                i += 1
            streamed += 1
        return res


