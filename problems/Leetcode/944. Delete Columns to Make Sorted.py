class Solution:
    def minDeletionSize(self, strs: List[str]) -> int:
        res = 0
        for i in range(max(len(s) for s in strs)):
            prev = 'a'
            for r in range(len(strs)):
                s = strs[r]
                if s[i] < prev:
                    res += 1
                    break
                prev = s[i]
        return res
                