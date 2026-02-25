import sortedcontainers

class Solution:
    def numberOfPairs(self, nums1: List[int], nums2: List[int], diff: int) -> int:

        # nums1[i] - nums2[i] <= nums1[j] - nums2[j] + diff
        n = len(nums1)
        arr = [ nums1[i] - nums2[i] for i in range(n) ]

        res = 0
        sl = SortedList(arr)
        for i in range(n):
            v = arr[i]
            sl.remove(v)
            lowestAllowed = v - diff
            # count >= lowestAllowed
            count = len(sl) - sl.bisect_left(lowestAllowed)
            res += count
        
        return res
