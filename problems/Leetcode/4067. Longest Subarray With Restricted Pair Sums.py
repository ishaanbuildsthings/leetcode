# Wrong Answer
# 7 / 634 testcases passed
# Input
# nums =
# [3,1,2]
# Use Testcase
# Output
# 3
# Expected
# 2
class Solution:
    def maxSubarray(self, nums: List[int]) -> int:
        res = 0
        n = len(nums)
        l = r = 0
        c = Counter()
        mx = max(nums)
        pairs = Counter() # pairs sums

        # do we have a pair summing to this?
        def isBad(val):
            for pair in pairs:
                if pairs[pair] and c[pair]:
                    return True
            return False

        while r < n:
            v = nums[r]
            for single, frq in c.items():
                pairSum = single + v
                if pairSum <= mx:
                    pairs[pairSum] += frq
            c[v] += 1

            # print(f'{v=}')
            # print(f'{c=}')
            # print(f'{pairs=}')
            # print(f'{c=}')
            while isBad(v):
                # print(f'is bad')
                lost = nums[l]
                # print(f'losing: {lost}')
                
                for single, frq in c.items():
                    pairSum = lost + single
                    if pairSum <= mx:
                        lostFrq = frq if single != lost else frq - 1
                        pairs[pairSum] -= lostFrq

                c[lost] -= 1
                    
                l += 1
                
            res = max(res, r - l + 1)
            r += 1

        return res
            
























        
        # mx = max(nums)
        # rightmost = {}

        # lefts = [None] * n # for every r, how far left can we go
        # for i in range(n):
        #     lefts[i] = i
        
        # for r in range(n):
        #     v = nums[r]
        #     rightmost[v] = r

        #     leftBad = inf

        #     for a in range(1, v):
        #         b = v - a

        #         if a not in rightmost:
        #             continue
        #         if b not in rightmost:
        #             continue

        #         right = max(rightmost[a], rightmost[b])
        #         leftBad = min(leftBad, right)

        #     lefts[r] = max(lefts[r], leftBad + 1)

        # print(lefts)

        # return res
            
            