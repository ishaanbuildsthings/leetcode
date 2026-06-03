class Solution:
    def longestCommonSubsequence(self, arrays: List[List[int]]) -> List[int]:
        c = defaultdict(lambda: float('inf'))
        seen = set(num for arr in arrays for num in arr)
        for arr in arrays:
            arrCount = Counter(arr)
            for key in seen:
                c[key] = min(c[key], arrCount[key])
        res = []
        for key in sorted(c.keys()):
            res.extend([key] * c[key])
        return res