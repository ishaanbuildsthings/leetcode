class Solution:
    def maxRemovals(self, source: str, pattern: str, targetIndices: List[int]) -> int:
        idxSet = set(targetIndices)
        
        @cache
        def dp(i, j):
            if i == len(source):
                return 0 if j == len(pattern) else -inf
            if j == len(pattern):
                return int(i in idxSet) + dp(i + 1, j)
                
            noRemove = dp(i + 1, j + int(source[i] == pattern[j]))
            if i in idxSet:
                ifRemove = 1 + dp(i + 1, j)
                return max(ifRemove, noRemove)
            return noRemove
            
        return dp(0, 0)
        dp.cache_clear()
        return r
            