# SOLUTION 1, O(n^2 log max)
# we alien trick to find the max penalty where we still want >= k partitions
# also if with no penalty we take < k partitions we accept that too since the question asks for at most k
# we test every rotation, TLE in everything except C++ where we do bottom up dp
# fmax = lambda x, y: x if x > y else y
# class Solution:
#     def maximumScore(self, nums: List[int], k: int) -> int:
#         n = len(nums)
        
#         def withPenalty(y, arr):
#             # state 0 means didn't pick min or max
#             # state 1 means picked min only
#             # state 2 means picked max only
#             # no state 3, we would just transition to state 0 immediately

#             # returns min cost, partitions used
#             cache = [[None] * 3 for _ in range(len(arr))]
#             def dp(i, state):
#                 if i == n:
#                     if state != 0:
#                         # at the end we need to be in state 0, we cannot pick just a min or max
#                         # but if we let the last partition exist but not pick any (state 0)
#                         # that's ok, because we basically scored 0 from that subarray
#                         return (-inf, -inf)
#                     return (0, 0)
#                 if cache[i][state] is not None:
#                     return cache[i][state]
#                 v = arr[i]
#                 if state == 0:
#                     ifCont = dp(i + 1, 0)
#                     ifMin = (-v - y + dp(i + 1, 1)[0], dp(i + 1, 1)[1] + 1)
#                     ifMax = (v - y + dp(i + 1, 2)[0], dp(i + 1, 2)[1] + 1)
#                     ans = fmax(ifCont, fmax(ifMin, ifMax))
#                 if state == 1:
#                     ifCont = dp(i + 1, 1)
#                     ifClose = (v + dp(i + 1, 0)[0], dp(i + 1, 0)[1])
#                     ans = fmax(ifCont, ifClose)
#                 if state == 2:
#                     ifCont = dp(i + 1, 2)
#                     ifClose = (-v + dp(i + 1, 0)[0], dp(i + 1, 0)[1])
#                     ans = fmax(ifCont, ifClose)
#                 cache[i][state] = ans
#                 return ans

#             res = dp(0, 0)
#             return res
        
#         # for a given cyclic rotation, perform an n log n WQS binary search
#         def fn(arr):
#             # if we naturally did not even want > k partitions with no penalty
#             # then if we binary search for the largest penalty where we want >= k partitions
#             # we never find any and return None
#             # since we are allowed to use <k partitions in this problem, we do it this way
#             val0, cnt0 = withPenalty(0, arr)
#             if cnt0 <= k:
#                 return val0
#             l = 0
#             r = max(arr) - min(arr)
#             resHere = None
#             while l <= r:
#                 y = (l + r) // 2
#                 val, cnt = withPenalty(y, arr)
#                 candidate = val + y * k
#                 if cnt >= k:
#                     resHere = candidate
#                     l = y + 1
#                 else:
#                     r = y - 1
#             return resHere
        
#         answer = -inf
#         for i in range(n):
#             arr = nums[i:] + nums[:i]
#             answer = fmax(answer, fn(arr))
        
#         return answer


# solution 2, dnc dp but we observe only two required arrays (TLE in python, worked in C++)
# O(n^2 + nk log n)
class Solution:
    def maximumScore(self, inputNums: List[int], k: int) -> int:
        n = len(inputNums)
        def solve(nums):
            dp = [[-inf] * (k + 1) for _ in range(n)]

            score = [[0] * n for _ in range(n)]
            for l in range(n):
                mx = -inf
                mn = inf
                for r in range(l, n):
                    mx = max(mx, nums[r])
                    mn = min(mn, nums[r])
                    score[l][r] = mx - mn

            for i in range(n):
                dp[i][1] = score[0][i]
            # dp[i][k] is the number of ways to form k partitions with elements 0...i
            for partitions in range(2, k + 1):
                
                def solveFn(fillL, fillR, leftJ, rightJ):
                    if fillL > fillR: return
                    mid = (fillR + fillL) // 2

                    bestScore = -inf
                    bestJ = None
                    for j in range(leftJ, min(rightJ + 1, mid + 1)):
                        scoreHere = score[j][mid] + (dp[j-1][partitions-1] if j else 0)
                        if scoreHere > bestScore:
                            bestScore = scoreHere
                            bestJ = j

                    dp[mid][partitions] = bestScore

                    solveFn(fillL, mid - 1, leftJ, bestJ)
                    solveFn(mid + 1, fillR, bestJ, rightJ)

                solveFn(0, n - 1, 0, n - 1) 
            
            return max([dp[n - 1][i] for i in range(k + 1)])
            
        idx = inputNums.index(min(inputNums))
        arr1 = inputNums[idx:] + inputNums[:idx]
        arr2 = inputNums[idx+1:] + inputNums[:idx+1]
        return max(solve(arr1), solve(arr2))            
