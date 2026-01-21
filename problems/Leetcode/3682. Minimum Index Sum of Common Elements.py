class Solution:
    def minimumSum(self, nums1: List[int], nums2: List[int]) -> int:
        res = inf
        early2 = {}
        for i, v in enumerate(nums2):
            if v not in early2:
                early2[v] = i
        
        for i, v in enumerate(nums1):
            if v in early2:
                res = min(res, i + early2[v])
        
        return res if res != inf else -1