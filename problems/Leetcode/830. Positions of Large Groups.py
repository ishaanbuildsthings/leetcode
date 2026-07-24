class Solution:
    def largeGroupPositions(self, s: str) -> List[List[int]]:
        res = []
        streak = 1
        curr = s[0]
        for i in range(1, len(s)):
            c = s[i]
            if c == curr:
                streak += 1
                continue
            if streak <= 2:
                streak = 1
                curr = c
                continue
            r = i - 1
            l = r - streak + 1
            res.append([l, r])
            streak = 1
            curr = c
        if streak >= 3:
            r = len(s) - 1
            l = r - streak + 1
            res.append([l, r])
        return res