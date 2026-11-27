class Solution:
    def countTrapezoids(self, points: List[List[int]]) -> int:

        @cache
        def g(x, y):
            return gcd(x, y)
            
# Given 2 different points, computes a slope as a fraction in gcd form (avoids precision)
# Any 2 points with the same slope will have the same output for this
        import math
        # [(x1, y1), (x2, y2)]
        def pointsToHashableSlope(p1, p2):
            x1, y1 = p1
            x2, y2 = p2
            rise = y2 - y1
            run = x2 - x1
            if not run:
                return (1, 0)
            if not rise:
                return (0, 1)
            common = math.gcd(rise, run)
            # always make run positive to hash (-1, 2) and (1, -2) to be the same thing
            if rise < 0:
                rise *= -1
                run *= -1
            return (rise // common, run // common)


        # ✅ Tested on https://leetcode.com/problems/count-number-of-trapezoids-ii/solutions/
        # ⚠️ Not constant optimized

        # For any two different points, get a normalized line, if two other points are on that line, they will produce the same one
        # [(x1, y1), (x2, y2)]
        # O(log(max coordinate)) for the gcd
        def pointsToNormalLine(p1, p2):
            x1, y1 = p1
            x2, y2 = p2
            rise = y2 - y1
            run = x2 - x1

            if not rise:
                return (0, 1, -y1)
            if not run:
                return (1, 0, -x1)

            # We will solve Ax + By + C = 0 (normal form of a line)
            # kind of like y = mx + b, see: By = -Ax - C
            # Because both points lie on the same line we have:
            # (Ax_2 + By_2 + C) - (Ax_1 + By_1 + C) = 0 (any point on the line formed by these two points would yield 0)
            # A(x_2 - x_1) + B(y_2 - y_1) = 0
            # A*run + B*rise = 0
            # one simple option is A=-rise, B=run
            # to make the triple (A, B, C) unique, we use gcd also
            common = math.gcd(rise, run)
            A = -1 * (rise // common)
            B = run // common
            # Solve for C (can rearrange equation), and use either p1 or p2
            C = -1 * (A*x1) - (B*y1)

            # now we have A, B, C, but need to dedupe with (-A, -B, -C)
            if A < 0:
                A *= -1
                B *= -1
                C *= -1
            return (A, B, C)

    
            # if not x:
            #     return inf
            # return y / x

        # def area(p1,p2,p3,p4):
        #     x1, y1 = p1
        #     x2, y2 = p2
        #     x3, y3 = p3
        #     x4, y4 = p4
        #     return abs(x1 * y2 - y1 * x2 + x2 * y3 - y2 * x3 + x3  * y4 -y3 * x4 + x4 * y1 - y4 * x1)
        #     # return abs()


        res = 0
        # map slope -> segments
        # for a given slope, go over all segments which is n^2 amortized total
        # for each segment update a counter of normalized line -> count of segments
        # then again for each normal line type, multiply with all other normal line types

        slopeToSeg = defaultdict(list)
        for i in range(len(points)):
            for j in range(i + 1, len(points)):
                p1, p2 = points[i], points[j]
                slope = pointsToHashableSlope(p1, p2)
                slopeToSeg[slope].append((p1, p2))

        for slope in slopeToSeg:
            segmentsWithThatSlope = slopeToSeg[slope]
            normalLineToCount = Counter()
            totalCount = 0
            for x, y in segmentsWithThatSlope:
                normalLine = pointsToNormalLine(x, y)
                normalLineToCount[normalLine] += 1
                totalCount += 1
            for normalLineType, normalLineCount in normalLineToCount.items():
                otherCount = totalCount - normalLineCount
                ways = otherCount * normalLineCount
                res += ways

        # midpoints = []
        midpointAndSlopeToCount = defaultdict(lambda: defaultdict(int)) # maps [midpoint][normal slope] -> count
        # for every pair, we get its midpoint and store that midpoint has been seen
        # will use this to calculate # of parallelograms
        # but any two points with the same midpoint and normal line, we cannot count
        for i in range(len(points)):
          p1 = points[i]
          x1,y1 = p1
          for j in range(i + 1, len(points)):
              p2 = points[j]
              x2,y2 = p2
              md = (x1+x2,y1+y2)
              # midpoints.append(md)
              normal = pointsToNormalLine(p1, p2)
              midpointAndSlopeToCount[md][normal] += 1
    # midpoints = list(set(midpoints))

        parallel = 0
        # for each midpoint, for which there are n^2
        # we know total # of segments with that midpoint
        # we can form pairs of segments
        # for each count in (midpoint, slope) we subtract those pairs
        for midpoint in midpointAndSlopeToCount:
            totalSegsWithMidpoint = 0
            for slope, segsWithMidpointAndSlope in midpointAndSlopeToCount[midpoint].items():
                totalSegsWithMidpoint += segsWithMidpointAndSlope
            totalSegPairs = (totalSegsWithMidpoint) * (totalSegsWithMidpoint-1) // 2
            for slope, segsWithMidpointAndSlope in midpointAndSlopeToCount[midpoint].items():
                miniSegPairs = (segsWithMidpointAndSlope) * (segsWithMidpointAndSlope-1) // 2
                totalSegPairs -= miniSegPairs
            parallel += totalSegPairs

        print(f'parallel: {parallel}')

        
                  
        

        g.cache_clear()
        
        return (res // 2) - (parallel)