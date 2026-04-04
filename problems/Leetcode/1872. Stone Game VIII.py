class Solution:
    def stoneGameVIII(self, stones: List[int]) -> int:

        # naive O(n^2) dp with turn param
        # pf = []
        # curr = 0
        # for v in stones:
        #     curr += v
        #     pf.append(curr)
        
        # # memo[i] tells us the answer to that subproblem
        # @cache
        # def dp(i, alice):
        #     if i == len(stones):
        #         return 0
        #     leftStone = pf[i - 1] if i else 0
        #     if alice:
        #         res = -inf
        #         tot = 0 if i else stones[0] # edge cause cause when we start we must pick >1 stone
        #         for j in range(i if i else 1, len(stones)):
        #             tot += stones[j]
        #             picked = tot + leftStone
        #             nscore = picked + dp(j + 1, False)
        #             res = max(res, nscore)
        #         return res
            
        #     res = inf
        #     tot = 0 if i else stones[0] # edge cause cause when we start we must pick >1 stone
        #     for j in range(i if i else 1, len(stones)):
        #         tot += stones[j]
        #         picked = tot + leftStone
        #         nscore = -picked + dp(j + 1, True)
        #         res = min(res, nscore) # note we MINIMIZE here, even though the dp represents alice's max score
        #         # cause bob is a minimizer
            
        #     return res
        
        # return dp(0, True)






        # Solution 2, O(n) top down dp with cached loop
        # pf = []
        # curr = 0
        # for v in stones:
        #     curr += v
        #     pf.append(curr)
        
        # @cache
        # def loop(i, alice):
        #     if i == len(stones):
        #         return -inf if alice else inf # crucial, not needed in the naive top down dp because it means there were truly no stones left
        #         # but here, it symbolizes we are looping on how many to select, and if we return 0 here
        #         # it ends up being an escape hatch for the players, like you keep looping until you get to 0
        #     gain = pf[i - 1] + stones[i]
        #     if not alice:
        #         gain *= -1
        #     ifStopHere = gain + dp(i + 1, not alice)
        #     fn = max if alice else min
        #     ifCont = loop(i + 1, alice)
        #     return fn(ifCont, ifStopHere)
        
        # # memo[i] tells us the answer to that subproblem
        # @cache
        # def dp(i, alice):
        #     if i == len(stones):
        #         return 0
        #     if i == 0:
        #         return loop(i + 1, alice)
        #     return loop(i, alice)
                    
        # return dp(0, True)






        # Solution 3, top down O(n) with cached loop, no player param
        # we can use no player param when games are symmetrics 
        # pf = []
        # curr = 0
        # for v in stones:
        #     curr += v
        #     pf.append(curr)

        # @cache
        # def loop(i):
        #     if i == len(stones):
        #         return -inf # maximize my advantage against the other player, whoever i am, but remember this is not an escape hatch
        #     before = pf[i - 1]
        #     gainHere = before + stones[i] - dp(i + 1)
        #     ifCont = loop(i + 1)
        #     return max(gainHere, ifCont)
        
        # @cache
        # def dp(i):
        #     if i == len(stones):
        #         return 0
        #     return loop(i if i else i + 1)
        
        # return dp(0)




        # Soltuion 4, bottom up dp with no turn param O(n^2)
        # note I did this ternary - (dp[j + 1] if j + 1 < len(stones) else 0))
        # but we could have made the dp array bigger, or done some exlcusive prefix/suffixing (probably)
        # dp = [-inf] * len(stones)
        # pf = []
        # curr = 0
        # for v in stones:
        #     curr += v
        #     pf.append(curr)
        
        # for i in range(len(stones) - 1, -1, -1):
        #     for j in range(i, len(stones)):
        #         dp[i] = max(dp[i], pf[j] - (dp[j + 1] if j + 1 < len(stones) else 0))
        
        # return dp[1]



        # Solution 5, bottom up dp with no turn param, O(n)
        # note that dp[i] means we are considering any options from i..., NOT that we are solving the i... array problem
        # this is why we return dp[1] (since the 0th index is never a first option, as that would only select 1 stone)
        # the max(..., dp[i+1]) is almost like the suffix cached loop, built into the dp
        pf = []
        curr = 0
        for v in stones:
            curr += v
            pf.append(curr)
        dp = [-inf] * len(stones)
        dp[-1] = sum(stones)
        for i in range(len(stones) - 2, -1, -1):
            dp[i] = max(pf[i] - (dp[i + 1]), dp[i + 1])
        return dp[1]




            
            