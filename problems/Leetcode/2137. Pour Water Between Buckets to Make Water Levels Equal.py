class Solution:
    def equalizeWater(self, buckets: List[int], loss: int) -> float:
        l = min(buckets)
        r = max(buckets)
        res = l
        EPSILON = 1 / (10**5)

        # can we make all buckets have >= X?
        def canDo(x):
            receive = [v for v in buckets if v < x]
            give = [v for v in buckets if v >= x]
            donated = sum(v - x for v in give)
            requiredReceive = sum(x - v for v in receive)
            return (donated * (100 - loss) / 100) >= requiredReceive

        while l + EPSILON <= r:
            m = (l + r) / 2
            if canDo(m):
                res = m
                l = m
            else:
                r = m
        return res
