# Input
# s =
# "qo"
# t =
# "o"
# Use Testcase
# Output
# true
# Expected
# false



# Runtime Error
# 30 / 999 testcases passed
# IndexError: string index out of range
#          ~^^^
#     sc = s[i]
# Line 24 in canMakeSubsequence (Solution.py)
#     ret = Solution().canMakeSubsequence(param_1, param_2)
# Line 140 in _driver (Solution.py)
#     ~~~~~~~^^
#     _driver()
# Line 155 in <module> (Solution.py)
# Last Executed Input
# Use Testcase
# s =
# "op"
# t =
# "opoqm"


class Solution:
    def canMakeSubsequence(self, s: str, t: str) -> bool:


        # for every t, how much s can we consume
        consume = [] # can consume up to and including this, or -1
        i = 0 # we cannot consume this

        
        for j in range(len(t)):
            if i == len(s):
                consume.append(i - 1)
                continue
            tc = t[j]
            sc = s[i]
            if tc == sc:
                i += 1
            consume.append(i - 1)

        # print(consume)


        suffConsume = [None] * len(t)
        # suffConsume[j] means we can consume from i... onwards in s, or len(s) if not doable
        i = len(s) - 1
        for j in range(len(t) - 1, -1, -1):
            tc = t[j]
            sc = s[i]
            if tc == sc:
                i -= 1
            suffConsume[j] = i + 1

        # print(suffConsume)

        # print(t[:-1])

        for j in range(len(t) - 1):
            pfConsumed = consume[j]
            suffConsumed = suffConsume[j + 1]
            if pfConsumed + 1 == suffConsumed:
                print(f'edge to edge')
                return True

        # loop over parititons of t with a gap in the middle
        # if we consume s except for 1 letter, we can change the gap to that letter
        for j in range(1, len(t) - 1):
            pfConsumed = consume[j - 1]
            suffConsumed = suffConsume[j + 1]
            if abs(suffConsumed - pfConsumed) <= 2:
                return True

        def isSubseq(big, small):
            i = 0
            j = 0
            while i < len(big):
                if big[i] == small[j]:
                    j += 1
                if j == len(small):
                    return True
                i += 1
            return False

        if len(s) == 1:
            return True

        # if we change the first letter of t to match s[0]
        if len(t) > 1 and isSubseq(t[1:], s[1:]):
            print(f'true from change first')
            return True

        # or the last
        if len(t) > 1 and isSubseq(t[:-1], s[:-1]):
            print(f'true from last')
            return True

        if isSubseq(t, s):
            print(f'true from full subseq')
            return True
        
        return False
            
            

        # @cache
        # def dp(i, j, used):
        #     if i == len(s):
        #         return True
        #     if j == len(t):
        #         return False
        #     if s[i] == t[j]:
        #         return dp(i + 1, j + 1, used)
        #     # if not equal we skip t
        #     if used:
        #         return dp(i, j + 1, used)
        #     skipT = dp(i, j + 1, used)
        #     change = dp(i + 1, j + 1, True)
        #     return skipT or change

        # ans = dp(0,0,False)
        # dp.cache_clear()
        # return ans