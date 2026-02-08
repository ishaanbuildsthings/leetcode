 class Solution:
    def mergeAdjacent(self, nums: List[int]) -> List[int]:
        stack = []
        for i, v in enumerate(nums):
            curr = v
            while stack and stack[-1] == curr:
                curr += stack.pop()
            stack.append(curr)
        return stack