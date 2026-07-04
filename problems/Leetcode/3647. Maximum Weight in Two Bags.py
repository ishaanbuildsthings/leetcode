class Solution:
    def maxWeight(self, weights: List[int], w1: int, w2: int) -> int:
        
        # O(n * w1 * w2) normal dp

        # dp = [[False] * (w2 + 1) for _ in range(w1 + 1)]
        # dp[0][0] = True
        # # dp[curr1][curr2] tells us if that weight is achieveable

        # for i in range(len(weights)):
        #     w = weights[i]
        #     for weight1 in range(w1, -1, -1):
        #         for weight2 in range(w2, -1, -1):
        #             if dp[weight1][weight2]: continue

        #             if w <= weight1:
        #                 oldDp1 = dp[weight1 - w][weight2]
        #                 if oldDp1:
        #                     dp[weight1][weight2] = True
                    
        #             if w <= weight2:
        #                 oldDp2 = dp[weight1][weight2 - w]
        #                 if oldDp2:
        #                     dp[weight1][weight2] = True
        
        # res = 0
        # for weight1 in range(w1 + 1):
        #     for weight2 in range(w2 + 1):
        #         if dp[weight1][weight2]:
        #             res = max(res, weight1 + weight2)
        
        # return res


        # O(n * w1 * w2 / 64) dp
        # dp[curr1] = a bitset of reachable weight2s
        dp = [0] * (w1 + 1)
        dp[0] = 1
        fmask = (1 << (w2 + 1)) - 1
        for w in weights:
            for nw1 in range(w1, -1, -1):
                nmask = dp[nw1]
                # if we added this weight to bag2
                nmask |= (nmask << w)
                # if we added this weight to bag1
                if nw1 >= w:
                    nmask |= dp[nw1 - w]
                nmask &= fmask
                dp[nw1] = nmask
        
        res = 0
        for weight1 in range(w1 + 1):
            mask = dp[weight1]
            if mask:
                msb = mask.bit_length() - 1
                res = max(res, msb + weight1)
            
        return res
                