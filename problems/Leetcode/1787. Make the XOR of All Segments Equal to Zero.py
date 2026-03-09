class Solution:
    def minChanges(self, nums: List[int], k: int) -> int:
        dp = [inf] * 1024 # dp[xor] is the min number of elements we need to change to make our prefix equal to that xor, for the current elements we have processed
        dp[0] = 0

        groups = [[] for _ in range(k)] # index % k -> numbers in that group
        for i in range(len(nums)):
            group = i % k
            groups[group].append(nums[i])
        
        groupCounts = [Counter(groups[i]) for i in range(k)] # groupCounts[group][number] -> how many of that number in the group

        # every element in a group needs to be the same

        # process every index of a given group at the same time
        for i in range(k):
            ndp = [inf] * 1024

            prevBest = min(dp)

            # assume we overwrite every single element in this group with cost len(group), then we can just get our new xor to whatever we want
            for newXor in range(1024):
                ndp[newXor] = len(groups[i]) + prevBest
            
            # or we set all elements in this group, to an element already in the group
            for element, frq in groupCounts[i].items():
                cost = len(groups[i]) - frq
                for prevXor in range(1024):
                    newXor = prevXor ^ element
                    ndp[newXor] = min(ndp[newXor], dp[prevXor] + cost)
            
            dp = ndp
        
        return dp[0]