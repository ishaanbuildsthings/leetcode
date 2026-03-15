class Solution:
    def minimumLines(self, s: List[List[int]]) -> int:
        s.sort()
        return (len(s) > 1) + sum(
            (s[i+1][1] - s[i][1]) * (s[i+2][0] - s[i+1][0]) != (s[i+2][1] - s[i+1][1]) * (s[i+1][0] - s[i][0])
            for i in range(len(s) - 2)
        )