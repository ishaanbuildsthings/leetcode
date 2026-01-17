class Solution:
    def minOperations(self, nums: List[int], target: List[int]) -> int:
        uniq = set()
        for i in range(len(nums)):
            if nums[i] != target[i]:
                uniq.add(nums[i])
        return len(uniq)