class Solution:
    def largestUniqueNumber(self, nums: List[int]) -> int:
        # can use bucketing since range is limited lol
        c = Counter(nums)
        for big in sorted(c.keys(), reverse=True):
            if c[big] == 1:
                return big
        return -1