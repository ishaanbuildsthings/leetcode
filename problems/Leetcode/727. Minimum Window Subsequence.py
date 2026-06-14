from copy import copy

class Solution:
    def minWindow(self, s1: str, s2: str) -> str:

        # each index should store the closest right index for a given future letter
        onRightClosest = defaultdict(lambda: defaultdict(lambda: inf)) # maps (i : {letter:index})

        ABC = 'abcdefghijklmnopqrstuvwxyz'

        onRight = {
            c : inf for c in ABC
        }

        for i in range(len(s1) - 1, -1, -1):
            onRightClosest[i] = copy(onRight)
            onRight[s1[i]] = i

        @cache # cpu speedup
        def solve(i, j):
            if i == inf:
                return None
            if j == len(s2):
                return i # the index past the ending
            if i == len(s1):
                return None
            if s1[i] == s2[j]:
                return solve(i + 1, j + 1)
            nextPos = onRightClosest[i][s2[j]]
            return solve(nextPos, j)
        
        minSize = inf
        resL, resR = None, None
        for start in range(len(s1) - len(s2) + 1):
            res = solve(start, 0)
            if res == None:
                continue
            end = res - 1
            width = end - start + 1
            if width < minSize:
                minSize = width
                resL = start
                resR = end
        return s1[resL:resR+1] if minSize != inf else ''