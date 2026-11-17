class Solution:
    def isConvex(self, points: list[list[int]]) -> bool:
        
        def isLeftTurn(a, b, c):
            xdiff = b[0] - a[0]
            # arrow is pointing right
            if xdiff > 0:
                # compute a->b line formula, y = mx + b
                # b = y - mx
                slopeB = (b[1] - a[1]) / (b[0] - a[0])
                B = a[1] - slopeB * a[0]

                # at c's x, where is this line
                lineY = slopeB * c[0] + B

                # on the line
                if lineY == c[1]:
                    return None
                
                return c[1] > lineY
            
            if xdiff == 0:
                if c[0] == a[0]:
                    return None
                # if arrow goes straight up, check if C is on the left
                if a[1] < b[1]:
                    return c[0] < a[0]
                else:
                    return c[0] > a[0]
            
            # arrow points left
            # compute a->b line formula, y = mx + b
            # b = y - mx
            slopeB = (b[1] - a[1]) / (b[0] - a[0])
            B = a[1] - slopeB * a[0]

            # at c's x, where is this line
            lineY = slopeB * c[0] + B

            # on the line
            if lineY == c[1]:
                return None
            
            # arrow points left, so below the line is our left
            return c[1] < lineY
        
        points.extend([points[0], points[1]])
        
        dirs = set()
        for i in range(len(points) - 2):
            p1, p2, p3 = points[i:i+3]
            res = isLeftTurn(p1,p2,p3)
            if res is None:
                continue
            dirs.add(res)
        
        return len(dirs) == 1