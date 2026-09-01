class Solution:
    def minCost(self, colors: str, neededTime: List[int]) -> int:

        # returns two things (minTime1, rightColor), (minTime2, differentRightColor)
        @cache
        def dp(i):
            if i == len(colors):
                return (0, -1), (0, 1)
            t = neededTime[i]
            v = colors[i]

            # these are thw two states the suffix can give me
            (time1, c1), (time2, c2) = dp(i + 1)

            # if our color is the same as the best next color, we must either pop ours and use that next color, or tack ours onto the second best, these both give the option ending with our balloon color though

            # for our 2nd best, we would necessarily pop ours and pair with 2nd best
            if v == c1:
                TIME_A = min(time2, time1 + t)
                COLOR_A = v

                TIME_B = time2 + t
                COLOR_B = c2

                return (TIME_A, COLOR_A), (TIME_B, COLOR_B)
            
            # if our color is different from the next best, we could pair our balloon onto that for the for sure new minimum time
            # for the second minimum time, we could pop our balloon and use the best one, these are going to be the top 2
            return (time1, v), (t + time1, c1)
        
        return dp(0)[0][0]
            
            
        
            



        # memo = [defaultdict(lambda: -1) for _ in range(len(colors))]
        # def dp(i, prevColor):
        #     # base
        #     if i == len(colors):
        #         return 0

        #     if memo[i][prevColor] != -1:
        #         return memo[i][prevColor]

        #     resThis = float('inf')
            
        #     # we can skip this if we are a different color
        #     if colors[i] != prevColor:
        #         resThis = dp(i + 1, colors[i])

        #     # we can remove this
        #     ifRemoveThis = neededTime[i] + dp(i + 1, prevColor)

        #     resThis = min(resThis, ifRemoveThis)
        #     memo[i][prevColor] = resThis
        #     return resThis
        
        # return dp(0, None)