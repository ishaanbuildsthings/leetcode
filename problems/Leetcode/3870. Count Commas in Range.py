class Solution:
    def countCommas(self, n: int) -> int:

        def go(v):
            if v < 1000:
                return 0
            if v < 1_000_000:
                return 1

        return sum(go(x) for x in range(1, n + 1))