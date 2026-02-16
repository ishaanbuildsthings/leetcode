class Solution:
    def smallerNumbersThanCurrent(self, nums: List[int]) -> List[int]:
        c = [0] * 101
        for v in nums:
            c[v] += 1
        for number in range(1, 101):
            c[number] += c[number - 1]
        res = [c[x-1] if x else 0 for x in nums]
        return res
        
