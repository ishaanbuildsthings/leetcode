class Solution:
    def shareCandies(self, candies: List[int], k: int) -> int:
        
        c = Counter(candies)
        for i in range(k):
            candy = candies[i]
            c[candy] -= 1
            if not c[candy]:
                del c[candy]
        res = len(c)
        for r in range(k, len(candies)):
            sheGains = candies[r]
            c[sheGains] -= 1
            if not c[sheGains]:
                del c[sheGains]
            l = r - k
            weGain = candies[l]
            c[weGain] += 1
            res = max(res, len(c))
        
        return res