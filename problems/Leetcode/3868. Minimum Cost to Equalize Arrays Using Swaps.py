class Solution:
    def minCost(self, nums1: list[int], nums2: list[int]) -> int:
        c1 = Counter(nums1)
        c2 = Counter(nums2)

        for num in nums1:
            if (c1[num] + c2[num]) % 2:
                return -1
        for num in nums2:
            if (c1[num] + c2[num]) % 2:
                return -1

        allNums = set()
        for v in nums1:
            allNums.add(v)
        for v in nums2:
            allNums.add(v)

        res = 0

        DIFFS = 0
        for v in allNums:
            f1 = c1[v]
            f2 = c2[v]
            diff = abs(f1 - f2)
            DIFFS += diff

        return DIFFS // 4
        