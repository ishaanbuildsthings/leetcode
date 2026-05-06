class Solution:
    def removeBoxes(self, boxes: List[int]) -> int:

        @cache
        def goRight(i):
            if i == len(boxes) - 1:
                return i
            if boxes[i + 1] != boxes[i]:
                return i
            return goRight(i + 1)
        
        @cache
        def dp(l, r, surplusLeft):
            if l > r:
                return 0
            # remove this left chain by itself
            rightmost = min(goRight(l), r) # tricky tricky we don't want to exceed r
            width = rightmost - l + 1
            totalSize = width + surplusLeft
            scoreGained = totalSize ** 2
            nxtDp = dp(rightmost + 1, r, 0)

            removeBySelf = scoreGained + nxtDp

            res = removeBySelf

            # or pair it with any other next run
            for R in range(rightmost + 1, r + 1):
                if boxes[R] == boxes[l]:
                    middleDp = dp(rightmost + 1, R - 1, 0)
                    onRightDp = dp(R, r, surplusLeft + width)
                    res = max(res, middleDp + onRightDp)
            
            return res

        return dp(0, len(boxes) - 1, 0)