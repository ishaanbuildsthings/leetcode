class Solution:
    def maximumProduct(self, nums: List[int]) -> int:
        big3 = heapq.nlargest(3, nums)
        small2 = heapq.nsmallest(2, nums)
        return max(big3[0] * big3[1] * big3[2], small2[0] * small2[1] * big3[0])