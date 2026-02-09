class Solution:
    def countMajoritySubarrays(self, nums: List[int], target: int) -> int:
        res = 0
        for l in range(len(nums)):
            c = Counter()
            for r in range(l, len(nums)):
                c[nums[r]] += 1
                if c[target] > (r - l + 1) / 2:
                    res += 1
        return res
