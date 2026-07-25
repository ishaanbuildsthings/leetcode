class Solution:
    def widestPairOfIndices(self, nums1: List[int], nums2: List[int]) -> int:
        arr = [nums1[i] - nums2[i] for i in range(len(nums1))]
        res = 0
        mp = {0:-1} # maps sum to leftmost index
        curr = 0
        for r in range(len(arr)):
            curr += arr[r]
            if curr in mp:
                left = mp[curr]
                width = r - left
                res = max(res, width)
            else:
                mp[curr] = r
        return res