class Solution:
    def shortestSubstrings(self, arr: List[str]) -> List[str]:
        res = []
        for i, w in enumerate(arr):
            others = [x for j, x in enumerate(arr) if j != i]
            shortest = ''
            for l in range(len(w)):
                for r in range(l, len(w)):
                    sub = w[l:r+1]
                    if any(sub in o for o in others):
                        continue
                    if shortest == '' or (len(sub), sub) < (len(shortest), shortest):
                        shortest = sub
            res.append(shortest)
        return res