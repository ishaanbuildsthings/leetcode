class Solution:
    def maxSumDistinctTriplet(self, x: List[int], y: List[int]) -> int:
        big = defaultdict(lambda: -inf)
        for i in range(len(x)):
            key = x[i]
            big[key] = max(big[key], y[i])

        vals = list(big.values())
        if len(vals) < 3:
            return -1

        vals.sort(reverse=True)
        return vals[0] + vals[1] + vals[2]
        # print(big)