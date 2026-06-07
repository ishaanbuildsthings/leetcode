class Solution:
    def findJudge(self, n: int, trust: List[List[int]]) -> int:
        trustedCounts = defaultdict(int)
        trustCounts = defaultdict(int)
        for a, b in trust:
            trustedCounts[b] += 1
            trustCounts[a] += 1
        for num in range(1, n + 1):
            if trustedCounts[num] == n - 1 and not trustCounts[num]:
                return num
        return -1