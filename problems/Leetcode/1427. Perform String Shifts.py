class Solution:
    def stringShift(self, s: str, shift: List[List[int]]) -> str:
        tot = 0
        for direction, diff in shift:
            tot += (-1 if not direction else 1) * diff
        tot %= len(s)
        if tot < 0:
            return s[abs(tot):] + s[:abs(tot)]
        return s[len(s) - tot:] + s[:len(s) - tot] 