class Solution:
    def minOperations(self, nums1: List[int], nums2: List[int], k: int) -> int:
        if sum(nums1) != sum(nums2): return -1
        if not k:
            if nums1 == nums2:
                return 0
            return -1
        res = 0
        for a, b in zip(nums1, nums2):
            diff = abs(a - b)
            if diff % k: return -1
            ops = diff // k
            res += ops
        return res // 2