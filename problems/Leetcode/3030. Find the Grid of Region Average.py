class Solution:
    def resultGrid(self, image: List[List[int]], threshold: int) -> List[List[int]]:
        h = len(image)
        w = len(image[0])

        def isRegion(r, c):
            for i in range(r, r + 3):
                for j in range(c, c + 3):
                    if i + 1 < r + 3 and abs(image[i][j] - image[i + 1][j]) > threshold:
                        return False
                    if j + 1 < c + 3 and abs(image[i][j] - image[i][j + 1]) > threshold:
                        return False
            return True

        # sum / 9
        def regionAvg(r, c):
            total = 0
            for i in range(r, r + 3):
                for j in range(c, c + 3):
                    total += image[i][j]
            return total // 9

        totSum = [[0] * w for _ in range(h)]
        countValid = [[0] * w for _ in range(h)]

        for r in range(h - 2):
            for c in range(w - 2):
                if isRegion(r, c):
                    avg = regionAvg(r, c)
                    for i in range(r, r + 3):
                        for j in range(c, c + 3):
                            totSum[i][j] += avg
                            countValid[i][j] += 1

        res = [[0] * w for _ in range(h)]
        for r in range(h):
            for c in range(w):
                if countValid[r][c] > 0:
                    res[r][c] = totSum[r][c] // countValid[r][c]
                else:
                    res[r][c] = image[r][c]

        return res