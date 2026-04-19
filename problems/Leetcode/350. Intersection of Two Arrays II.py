class Solution:
    def intersect(self, nums1: List[int], nums2: List[int]) -> List[int]:
        bigger = nums1 if len(nums1) >= len(nums2) else nums2
        smaller = nums1 if bigger == nums2 else nums2
        c = Counter(smaller)
        res = []
        for num in bigger:
            if c[num]:
                res.append(num)
                c[num] -= 1
        return res