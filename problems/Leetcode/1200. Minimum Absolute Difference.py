class Solution:
    def minimumAbsDifference(self, arr: List[int]) -> List[List[int]]:
        s = sorted(arr)
        # could do one pass but it would use more space as we would discard the result
        # could also use bucketing
        tiny = min(s[i] - s[i - 1] for i in range(1, len(s)))
        res = []
        for i in range(1, len(s)):
            if s[i] - s[i - 1] == tiny:
                res.append([s[i - 1], s[i]])
        return res
