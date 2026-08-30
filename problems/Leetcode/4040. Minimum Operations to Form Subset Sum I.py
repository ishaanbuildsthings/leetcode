# Input
# nums =
# [9,1,5]
# sum =
# 7
# Use Testcase
# Output
# 0
# Expected
# 1


class Solution:
    def minOperations(self, nums: list[int], sum: int) -> int:
        fmin = lambda x, y : x if x < y else y

        dp = [inf] * (sum + 1) # min ops to form this
        dp[0] = 0
        ndp = [inf] * (sum + 1)

        for i, v in enumerate(nums):
        
            for oldSum in range(sum + 1):
                # print(f'old sum is: {oldSum}')

                ndp[oldSum] = min(ndp[oldSum], dp[oldSum])

                options = []

                doubled = v
                for double in range(32):
                    if doubled + oldSum > sum:
                        break
                    options.append((doubled, double))
                    doubled *= 2

                half = v
                for halved in range(32):
                    # print(f'half is: {half}')
                    if half + oldSum > sum:
                        half //= 2
                        continue
                    options.append((half, halved))
                    if half == 0:
                        break
                    half //= 2

                # print(f'options: {options}')

                for diff, ops in options:
                    nsum = oldSum + diff
                    if nsum > sum:
                        continue
                    ndp[nsum] = fmin(ndp[nsum], dp[oldSum] + ops)


            dp, ndp = ndp, dp
            # print(f'dp after first layer: {dp}')

        answer = dp[sum]
        if answer == inf:
            return -1
        return answer
                    
                    
                

        
        # n = len(nums)

        # # 5 -> 10
        # # 6 -> 12

        # fmin = lambda x, y: x if x < y else y

        # SIZE = n * (sum + 1)

        # cache = [-1] * SIZE


        # # @cache
        # def dp(i, prevSum):
        #     # print(f'dp called on: {i=} {prevSum=}')
        #     if i == n:
        #         return 0 if prevSum == sum else inf
        #     key = (i * (sum + 1)) + prevSum
        #     if cache[key] != -1:
        #         return cache[key]


        #     currV = nums[i]
        #     res = inf
        #     for doubled in range(32):
        #         if currV + prevSum > sum:
        #             break
        #         # print(f'trying double: {currV}')
        #         score = doubled + dp(i + 1, currV + prevSum)
        #         currV *= 2
        #         res = fmin(res, score)

        #     currV = nums[i]
        #     # print(f'curr v: {currV}')
        #     for halved in range(32):
        #         if currV + prevSum > sum:
        #             currV //= 2
        #             continue
        #         # print(f'trying value: {currV} from halving')
        #         score = halved + dp(i + 1, currV + prevSum)
        #         res = fmin(res, score)
        #         if currV == 0:
        #             break
        #         currV //= 2

        #     ifSkip = dp(i + 1, prevSum)
        #     res = fmin(res, ifSkip)

        #     cache[key] = res

        #     return res

        # answer = dp(0,0)
        # # dp.cache_clear()
        # if answer == inf:
        #     return -1

        # return answer

            
                
                