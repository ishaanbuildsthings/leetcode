class Solution:
    def findLHS(self, nums: List[int]) -> int:
        c = Counter(nums)
        return max((c[num] + c[num + 1] for num in c if c[num] and c[num + 1]), default=0)