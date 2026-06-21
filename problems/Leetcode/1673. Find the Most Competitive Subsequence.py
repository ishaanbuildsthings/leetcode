class Solution:
    def mostCompetitive(self, nums: List[int], k: int) -> List[int]:
        stack = []
        for i in range(len(nums)):
            num = nums[i]
            while stack and num < stack[-1] and k - len(stack) < len(nums) - i:
                stack.pop()
            if len(stack) < k:
                stack.append(num)
        return stack
