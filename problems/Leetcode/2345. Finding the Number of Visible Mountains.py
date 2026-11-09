class Solution:
    def visibleMountains(self, peaks: list[list[int]]) -> int:
        bases = []
        for x, y in peaks:
            l = x - y
            r = x + y
            bases.append([l, r])
        bases.sort(key=lambda tup: (tup[0], -tup[1]))
        frq = Counter(tuple(x) for x in bases)
        # sl = SortedList()
        res = 0
        mx = -inf
        for l, r in bases:
            covered = mx >= r
            if not covered and frq[(l, r)] == 1:
                res += 1
            # sl.add(r)
            mx = max(mx, r)
        return res

        
        