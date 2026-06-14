from sortedcontainers import SortedList

class Solution:
    def minCost(self, arr: List[int], brr: List[int], k: int) -> int:
        res = inf
        
        noSplit = 0
        # if we dont split
        for i in range(len(arr)):
            diff = abs(arr[i] - brr[i])
            noSplit += diff
        
        res = noSplit
        
        a1 = sorted(arr)
        b1 = sorted(brr)
        split = k
        for i in range(len(a1)):
            split += abs(a1[i] - b1[i])
        
        res = min(res, split)
        return res
        
        # have 2, 4
        # want 3, 4
        # good assignment: 2, 4     3, 4
        # bad assignment: 4, 2    3, 4
        
        
        # have 3, 4
        # want 2, 4
        
        
        