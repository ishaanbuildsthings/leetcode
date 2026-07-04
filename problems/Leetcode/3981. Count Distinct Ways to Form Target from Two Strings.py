class Solution:
    def interleaveCharacters(self, word1: str, word2: str, target: str) -> int:            
        MOD = 10**9 + 7

        def subseq(word):
            @cache
            def fn(i, k):
                if k == len(target):
                    return 1
                if i == len(word):
                     return 0
                res = 0
                if word[i] == target[k]:
                    res += fn(i + 1, k + 1)
                ifSkip = fn(i + 1, k)
                res += ifSkip
                return res % MOD
            return fn(0, 0)

        @cache
        def dp(i, j, k, from1):
            if k == len(target):
                return 1

            c = target[k]
            res = 0

            if from1:
                if i == len(word1): return 0
                if word1[i] == c:
                    # basically at the last letter, we cant take it then open 2 new DPs, that double counts the base case
                    # so we only score 1, and then also add on the skip
                    if k == len(target) - 1: return 1 + dp(i + 1, j, k, True)
                    res += dp(i + 1, j, k + 1, True)
                    res += dp(i + 1, j, k + 1, False)
                # can always skip
                res += dp(i + 1, j, k, True)
            else:
                if j == len(word2): return 0
                if word2[j] == c:
                    if k == len(target) - 1: return 1 + dp(i, j + 1, k, False)
                    res += dp(i, j + 1, k + 1, True)
                    res += dp(i, j + 1, k + 1, False)
                # can always skip
                res += dp(i, j + 1, k, False)

            return res % MOD

        ans = (dp(0, 0, 0, True) + dp(0, 0, 0, False)) % MOD
        ans -= subseq(word1)
        ans -= subseq(word2)
        ans %= MOD
        return ans
        