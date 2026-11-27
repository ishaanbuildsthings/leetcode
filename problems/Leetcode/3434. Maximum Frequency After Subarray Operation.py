class Solution:
    def maxFrequency(self, nums: List[int], k: int) -> int:
        postfix = [None] * len(nums)
        curr = 0
        for i in range(len(nums) - 1, -1, -1):
            curr += nums[i] == k
            postfix[i] = curr

        def fn(added):
            resNotAddedYet = 0
            resAdding = 0
            resDoneAdding = 0
            for num in nums:
                newNoAdd = resNotAddedYet + int(num == k)
                newAdding = max(resNotAddedYet + int((num + added) == k), resAdding + int((num + added) == k))
                newDoneAdding = max(resDoneAdding + int(num == k), resAdding + int(num == k))
                resNotAddedYet = newNoAdd
                resAdding = newAdding
                resDoneAdding = newDoneAdding
            
            return max(resNotAddedYet, resAdding, resDoneAdding)
#             resHere = 0
#             @cache
#             def dp(i, stage):
#                 if i == len(nums):
#                     return 0
#                 if stage == 0:
#                     passOpt = dp(i + 1, 0) + (nums[i] == k)
#                     startAddingGain = int(nums[i] + added == k)
#                     openOpt = startAddingGain + dp(i + 1, 1)
#                     return max(passOpt, openOpt)
#                 elif stage == 1:
#                     contAddGain = int(nums[i] + added == k)
#                     closeGain = int(nums[i] == k)
#                     return max(contAddGain + dp(i + 1, 1), closeGain + dp(i + 1, 2))
#                 else:
#                     return postfix[i]
            
#             ans = dp(0, 0)
#             # print(f'{ans=}')
#             dp.cache_clear()
#             return ans
        
        res = 0
        small = 10**18
        big = -1 * small
        for num in nums:
            small = min(small, num)
            big = max(big, num)

        maxToAdd = k - small
        minSub = k - big
        c = Counter(nums)
        for addable in range(minSub - 1, maxToAdd + 1):
            if c[k] + c[k - addable] <= res:
                continue
            res = max(res, fn(addable))

        return res