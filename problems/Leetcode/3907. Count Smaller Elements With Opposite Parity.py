class Solution:
    def countSmallerOppositeParity(self, nums: list[int]) -> list[int]:
        o = SortedList()
        e = SortedList()
        res = [None] * len(nums)
        for i in range(len(nums) - 1, -1, -1):
            parity = nums[i] % 2
            sl = o if parity == 0 else e
            cnt = sl.bisect_left(nums[i])
            res[i] = cnt
            if nums[i] % 2:
                o.add(nums[i])
            else:
                e.add(nums[i])
        return res