class Solution:
    def minimumArrayLength(self, nums: List[int]) -> int:
        c = Counter(nums)
        mn = min(nums)
        frq = c[mn]
        for k in c:
            if k % mn != 0:
                return 1
        return math.ceil(frq / 2)

        # any bigger number can get nuked by a smaller number