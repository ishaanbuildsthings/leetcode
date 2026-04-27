class Solution:
    def maxDistance(self, side: int, points: List[List[int]], k: int) -> int:
        arr = []
        for x, y in points:
            # left edge
            if x == 0:
                arr.append(y)
            # top ledge
            elif y == side:
                arr.append(side + x)
            # right edge
            elif x == side:
                arr.append(2 * side + (side - y))
            # bottom edge
            else:
                arr.append(3 * side + (side - x))

        arr.sort()

        def canDo(dist):
            # try all starting points
            for i in range(len(arr)):
                start = arr[i]
                end = start + (4 * side) - dist # last pick can't exceed this
                cur = start
                picks = 1
                while picks < k:
                    idx = bisect_left(arr, cur + dist)
                    if idx == len(arr) or arr[idx] > end:
                        break
                    cur = arr[idx]
                    picks += 1
                if picks == k:
                    return True
            return False


        l = 0
        r = side
        res = None
        while l<=r:
            m = (r+l)//2
            if canDo(m):
                res = m
                l = m + 1
            else:
                r = m - 1
        
        return res
            
