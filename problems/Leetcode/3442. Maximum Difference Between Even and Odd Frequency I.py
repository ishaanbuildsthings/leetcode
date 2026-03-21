class Solution:
    def maxDifference(self, s: str) -> int:
        c = Counter(s)
        minOdd = inf
        maxOdd = -inf
        minE = inf
        maxE = -inf
        for key in c:
            if c[key] % 2:
                maxOdd=max(maxOdd,c[key])
                minOdd=min(minOdd,c[key])
            else:
                maxE=max(maxE,c[key])
                minE=min(minE,c[key])
        
        return maxOdd - minE