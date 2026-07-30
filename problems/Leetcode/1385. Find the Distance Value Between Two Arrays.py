class Solution:
    def findTheDistanceValue(self, arr1: List[int], arr2: List[int], d: int) -> int:
        arr2.sort()
        res = 0

        for a1 in arr1:
            # find smallest # >= a1 in arr2
            l = 0
            r = len(arr2) - 1
            resHere = None
            while l <= r:
                m = (r + l) // 2
                a2 = arr2[m]
                if a2 >= a1:
                    resHere = a2
                    r = m - 1
                else:
                    l = m + 1
            if resHere is not None:
                dist = resHere - a1
                if dist <= d:
                    continue
            
            # find the biggest # <= a1 in arr2
            l = 0
            r = len(arr2) - 1
            resHere = None
            while l <= r:
                m = (r + l) // 2
                a2 = arr2[m]
                if a2 <= a1:
                    resHere = a2
                    l = m + 1
                else:
                    r = m - 1
            if resHere is not None:
                dist = a1 - resHere
                if dist <= d:
                    continue
            
            
            res += 1
        
        return res