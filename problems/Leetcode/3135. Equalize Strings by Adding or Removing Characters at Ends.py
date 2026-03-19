class Solution:
    def minOperations(self, initial: str, target: str) -> int:
        # longest common substring at initial[i]... and target[j]..., must use i and j
        cache = [[-1 for _ in range(len(target))] for _ in range(len(initial))]
        def dp(i, j):
            if i == len(initial) or j == len(target):
                return 0
            if cache[i][j] != -1:
                return cache[i][j]
            if initial[i] == target[j]:
                ans = 1 + dp(i + 1, j + 1)
                cache[i][j] = ans
                return ans
            return 0
        longest = 0
        for i in range(len(initial)):
            for j in range(len(target)):
                longest = max(longest, dp(i, j))
        res = (len(initial) - longest) + (len(target) - longest)
        # dp.cache_clear()
        return res