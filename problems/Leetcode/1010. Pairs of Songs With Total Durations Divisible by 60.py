class Solution:
    def numPairsDivisibleBy60(self, time: List[int]) -> int:
        res = 0
        remain = defaultdict(int)
        for t in time:
            remainder = t % 60
            required = (60 - remainder) % 60
            res += remain[required]
            remain[remainder] += 1
        return res