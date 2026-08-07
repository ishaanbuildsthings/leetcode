class Solution:
    def countPairs(self, coordinates: List[List[int]], k: int) -> int:
        xToYCounter = defaultdict(Counter)
        res = 0
        for x, y in coordinates:
            for xxor in range(k + 1):
                yxor = k - xxor
                reqX = x ^ xxor
                reqY = y ^ yxor
                res += xToYCounter[reqX][reqY]
            xToYCounter[x][y] += 1
        return res