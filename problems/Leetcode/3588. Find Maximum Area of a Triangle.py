class Solution:
    def maxArea(self, coords: List[List[int]]) -> int:
        upX = defaultdict(lambda: -inf)
        downX = defaultdict(lambda: inf)
        leftY = defaultdict(lambda: inf)
        rightY = defaultdict(lambda: -inf)
        allX = set()
        allY = set()
        for x, y in coords:
            upX[x] = max(upX[x], y)
            downX[x] = min(downX[x], y)
            leftY[y] = min(leftY[y], x)
            rightY[y] = max(rightY[y], x)
            allX.add(x)
            allY.add(y)

        rightmost = -inf
        leftmost = inf
        topmost = -inf
        downmost = inf
        for x, y in coords:
            rightmost = max(rightmost, x)
            leftmost = min(leftmost, x)
            topmost = max(topmost, y)
            downmost = min(downmost, y)

        res = -1
        for x in allX:
            # print(f'x={x}------------')
            up = upX[x]
            down = downX[x]
            if up == down:
                continue
            base = up - down
            goRight = rightmost - x
            # print(f'go right: {goRight}')
            areaHere = base * goRight
            res = max(res, areaHere)
            goLeft = x - leftmost
            areaHere = base * goLeft
            res = max(res, areaHere)

        for y in allY:
            left = leftY[y]
            right = rightY[y]
            if left == right:
                continue
            base = right - left
            goUp = topmost - y
            areaHere = base * goUp
            res = max(res, areaHere)
            goDown = y - downmost
            areaHere = base * goDown
            res = max(res, areaHere)

        if res <= 0:
            return -1
        return res
            
        