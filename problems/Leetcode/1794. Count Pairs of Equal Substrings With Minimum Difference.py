class Solution:
    def countQuadruples(self, firstString: str, secondString: str) -> int:
        left1 = defaultdict(lambda : inf)
        right2 = defaultdict(lambda : -inf)
        for i, v in enumerate(firstString):
            left1[v] = min(left1[v], i)
        for i, v in enumerate(secondString):
            right2[v] = max(right2[v], i)
        resDist = inf
        
        for c in left1:
            dist = left1[c] - right2[c]
            resDist = min(resDist, left1[c] - right2[c])
        
        res = 0
        for i in range(len(firstString)):
            j = i + -1 * resDist
            if j >= len(secondString) or j < 0:
                continue
            res += firstString[i] == secondString[j]
        
        return res

