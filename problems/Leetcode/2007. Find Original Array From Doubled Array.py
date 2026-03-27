class Solution:
    def findOriginalArray(self, changed: List[int]) -> List[int]:
        c = Counter(changed)
        changed.sort()
        res = []
        for i in range(len(changed) -1, -1, -1):
            v = changed[i]
            if not c[v]:
                continue
            if v % 2:
                return []
            c[v] -= 1
            c[v // 2] -= 1
            if c[v // 2] < 0:
                return []
            res.append(v // 2)
        # dont think this if is needed
        if max(c.values()) == min(c.values()) == 0:
            return res
        return []