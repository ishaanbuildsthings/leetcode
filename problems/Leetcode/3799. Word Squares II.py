class Solution:
    def wordSquares(self, words: List[str]) -> List[List[str]]:
        res = []
        seen = set() # holds hash of sorted incies
        n = len(words)
        for top in range(n):
            for right in range(n):
                for bottom in range(n):
                    for left in range(n):
                        if len({top, right, bottom, left}) < 4:
                            continue
                        t = words[top]
                        r = words[right]
                        b = words[bottom]
                        l = words[left]
                        if t[-1] == r[0] and r[-1] == b[-1] and b[0] == l[-1] and l[0] == t[0]:
                            res.append([t, l, r, b])
        return sorted(res)