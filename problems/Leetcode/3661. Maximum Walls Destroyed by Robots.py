from sortedcontainers import SortedList
fmax = lambda x, y: x if x > y else y
fmin = lambda x, y: x if x < y else y
class Solution:
    def maxWalls(self, robots: List[int], distance: List[int], walls: List[int]) -> int:
        sl = SortedList()
        bl = sl.bisect_left
        br = sl.bisect_right
        def inRange(sl, a, b):
            return 0 if a > b else br(b)-bl(a)

        posDist = list(zip(robots, distance))
        posDist.sort()

        
        for v in walls:
            sl.add(v)

        n = len(robots)

        @cache
        def dp(i, didPrevShootRight, prevRightEnd):
            if i == n:
                return 0
            pos, d = posDist[i]
            lb = posDist[i-1][0] + 1 if i-1 >= 0 else -10000000000
            rb = posDist[i+1][0] - 1 if i+1 < n else 10000000000

            rightEnd = fmin(pos + d, rb)
            killRight = inRange(sl, pos, rightEnd)

            if didPrevShootRight and pos <= prevRightEnd:
                overlapEnd = fmin(prevRightEnd, rightEnd)
                if overlapEnd >= pos:
                    killRight -= inRange(pos, overlapEnd)
            takeRight = killRight + dp(i+1,True,rightEnd)


            leftStart = fmax(pos-d,lb)
            killLeft = inRange(sl,leftStart,pos)
            if didPrevShootRight:
                if prevRightEnd >= leftStart:
                    overlapStart = leftStart
                    overlapEnd = min(prevRightEnd, pos)
                    if overlapStart <= overlapEnd:
                        killLeft -= inRange(sl, overlapStart, overlapEnd)
            return fmax(takeRight, killLeft + dp(i+1,False,-10000000000))

        a = dp(0,False,-10000000000)
        dp.cache_clear()
        return a
            