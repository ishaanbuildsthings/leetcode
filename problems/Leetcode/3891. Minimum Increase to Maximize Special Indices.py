# SOLUTION 1, we have prefix and suffix arrays to tell us those scores, and choose where to put the gap of 2
# note that i=1 and i=n-3 are invalid places for a gap of 2 to start
# class Solution:
#     def minIncrease(self, nums: List[int]) -> int:
#         n = len(nums)

#         if n % 2:
#             res = 0
#             for i in range(1, n - 1, 2):
#                 m = nums[i]
#                 l = nums[i-1]
#                 r = nums[i+1]
#                 mx = max(l, r)
#                 if m > mx:
#                     continue
#                 nscore = mx + 1
#                 diff = nscore - m
#                 res += diff
#             return res

#         # even amount in the middle

#         # tight left #  1 | (2) 3 (4) 5 (6) 7 | 8
#         # tight right # 1 | 2 (3) 4 (5) 6 (7) | 8
#         # gap right #   1 | (2) 3 (4) 5 6 (7) | 8
#         # gap left #    1 | (2) 3 4 (5) 6 (7) | 8


#         # 56 | (97) 40 (79) 74 45 (101) 4 (84) | 102
#         # put the gap anywhere

        # def score(i):
        #     l = nums[i-1]
        #     r = nums[i+1]
        #     mx = max(l, r)
        #     req = mx + 1
        #     v = nums[i]
        #     if v >= req:
        #         return 0
        #     diff = req - v
        #     return diff

#         @cache
#         def pref(i):
#             if i <= 0:
#                 return 0
#             return score(i) + pref(i - 2)

#         @cache
#         def suff(i):
#             if i >= n - 1:
#                 return 0
#             return score(i) + suff(i + 2)

#         res = pref(-1) + suff(2) # gap at 0
#         res = min(res, pref(n - 3) + suff(n)) # gap at n - 2
        
#         for gapI in range(2, n - 3, 2):
#             res = min(res, pref(gapI-1) + suff(gapI + 2))

#         return res
            

# SOLUTION 2, we basically put the gap anywhere but use knapsack dp(i, skippedBool) to handle it
class Solution:
    def minIncrease(self, nums: List[int]) -> int:
        def score(i):
            l = nums[i-1]
            r = nums[i+1]
            mx = max(l, r)
            req = mx + 1
            v = nums[i]
            if v >= req:
                return 0
            diff = req - v
            return diff
        n = len(nums)
        if n % 2:
            return sum(score(i) for i in range(1, n, 2))
        
        @cache
        def dp(i, skipped):
            if i >= len(nums) - 1:
                return 0
            res = score(i) + dp(i + 2, skipped) # if we pick here
            if not skipped:
                skip = dp(i + 1, True)
                res = min(res, skip)
            return res
        
        return dp(1, False)
