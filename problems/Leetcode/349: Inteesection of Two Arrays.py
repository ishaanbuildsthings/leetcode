# https://leetcode.com/problems/intersection-of-two-arrays/?envType=daily-question&envId=2024-03-10
# difficulty: easy

# Solution
class Solution:
    def intersection(self, nums1: List[int], nums2: List[int]) -> List[int]:
        s = nums1 if len(nums1) <= len(nums2) else nums2
        l = nums1 if s == nums2 else nums2
        numSet = set(s)
        res = []
        for n in l:
            if n in numSet:
                res.append(n)
                numSet.remove(n)
        return res