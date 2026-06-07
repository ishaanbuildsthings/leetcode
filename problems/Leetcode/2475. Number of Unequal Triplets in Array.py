class Solution:
    def unequalTriplets(self, nums: List[int]) -> int:
        # n^2 time trivial
        # bucket sort is O(n)

        res = 0
        for i in range(len(nums)):
            for j in range(i + 1, len(nums)):
                for k in range(j + 1, len(nums)):
                    res += (nums[i] != nums[j]) and (nums[i] != nums[k]) and (nums[j] != nums[k])
        
        return res