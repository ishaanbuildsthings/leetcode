class Solution:
    def appealSum(self, s: str) -> int:
        res = 0
        c = Counter() # maps bitmask -> count of substrings with that bitmask, ending at r
        c[0] = 1 # empty string
        for i, v in enumerate(s):
            nc = Counter()
            nc[0] = 1
            for oldMask, oldCount in c.items():
                nmask = oldMask | (1 << (ord(v) - ord('a')))
                nc[nmask] += oldCount
            for mask, frq in nc.items():
                res += mask.bit_count() * frq
            c = nc
        return res