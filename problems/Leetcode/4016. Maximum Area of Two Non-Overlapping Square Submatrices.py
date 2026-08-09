# Wrong Answer
# 895 / 1000 testcases passed
# Input
# mat =
# [[1,0,1]]
# Use Testcase
# Output
# 0
# Expected
# 1


class Solution:
    def maxArea(self, mat: List[List[int]]) -> int:
        height = len(mat)
        width = len(mat[0])

        @cache
        def ul(r, c):
            v = mat[r][c]
            if v == 0:
                return 0
            left = ul(r, c - 1) if (c - 1) >= 0 else 0
            up = ul(r - 1, c) if (r - 1) >= 0 else 0
            upLeft = ul(r - 1, c - 1) if (r - 1) >= 0 and (c - 1) >= 0 else 0
            bottle = min(left, up, upLeft)
            return 1 + bottle

        @cache
        def ur(r, c):
            v = mat[r][c]
            if v == 0:
                return 0
            up = ur(r - 1, c) if (r - 1) >= 0 else 0
            right = ur(r, c + 1) if (c + 1) < width else 0
            upRight = ur(r - 1, c + 1) if (r - 1) >= 0 and (c + 1) < width else 0
            bottle = min(up, right, upRight)
            return 1 + bottle

        @cache
        def dr(r, c):
            v = mat[r][c]
            if v == 0:
                return 0
            down = dr(r + 1, c) if (r + 1) < height else 0
            right = dr(r, c + 1) if (c + 1) < width else 0
            downRight = dr(r + 1, c + 1) if (r + 1) < height and (c + 1) < width else 0
            bottle = min(down, right, downRight)
            return 1 + bottle

        maxLeft = [0] * width

        for c in range(width):
            mx = 0
            for r in range(height):
                mx = max(mx, ul(r, c))
            maxLeft[c] = max(mx, maxLeft[c - 1] if c else 0)

        maxRight = [0] * width
        for c in range(width - 1, -1, -1):
            mx = 0
            for r in range(height):
                mx = max(mx, ur(r, c))
            maxRight[c] = max(mx, maxRight[c + 1] if c + 1 < width else 0)

        maxUp = [0] * height
        for r in range(height):
            mx = 0
            for c in range(width):
                mx = max(mx, ul(r, c))
            maxUp[r] = max(mx, maxUp[r - 1] if r else 0)

        maxDown = [0] * height
        for r in range(height - 1, -1, -1):
            mx = 0
            for c in range(width):
                mx = max(mx, dr(r, c))
            maxDown[r] = max(mx, maxDown[r + 1] if r + 1 < height else 0)

        # print(maxLeft)
        # print(maxRight)

        res = 0
        for allLeft in range(width - 1):
            leftMx = maxLeft[allLeft]
            rightMx = maxRight[allLeft + 1]
            bottle = min(leftMx, rightMx)
            res = max(res, bottle)

        for allUp in range(height - 1):
            upMx = maxUp[allUp]
            downMx = maxDown[allUp + 1]
            bottle = min(upMx, downMx)
            res = max(res, bottle)

        ul.cache_clear()
        ur.cache_clear()
        dr.cache_clear()

        return (res**2)







                