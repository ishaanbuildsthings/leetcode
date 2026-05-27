class Solution:
    def advantageCount(self, nums1: List[int], nums2: List[int]) -> List[int]:
        nums1.sort()

        two = [(nums2[i], i) for i in range(len(nums2))]
        two.sort(reverse=True)
        l = 0
        r = len(nums1) - 1
        res = [None] * len(nums1)
        for num, i in two:
            # if bigger can beat it, put it
            if nums1[r] > num:
                res[i] = nums1[r]
                r -= 1
            else:
                res[i] = nums1[l]
                l += 1
        return res




        