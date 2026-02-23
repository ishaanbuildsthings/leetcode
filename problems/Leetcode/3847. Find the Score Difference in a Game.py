class Solution:
    def scoreDifference(self, nums: List[int]) -> int:
        s1 = 0
        s2 = 0
        active = 1

        def swap():
            nonlocal active
            if active == 1:
                active = 2
            else:
                active = 1

        for i in range(len(nums)):
            if nums[i] % 2:
                swap()
            if (i + 1) % 6 == 0:
                swap()
            if active == 1:
                s1 += nums[i]
            else:
                s2 += nums[i]

        return s1 - s2