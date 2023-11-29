# https://leetcode.com/problems/maximum-number-of-achievable-transfer-requests/description/
# tags: backtracking
# difficulty: hard

# Problem
# We have n buildings numbered from 0 to n - 1. Each building has a number of employees. It's transfer season, and some employees want to change the building they reside in.

# You are given an array requests where requests[i] = [fromi, toi] represents an employee's request to transfer from building fromi to building toi.

# All buildings are full, so a list of requests is achievable only if for each building, the net change in employee transfers is zero. This means the number of employees leaving is equal to the number of employees moving in. For example if n = 3 and two employees are leaving building 0, one is leaving building 1, and one is leaving building 2, there should be two employees moving to building 0, one employee moving to building 1, and one employee moving to building 2.

# Return the maximum number of achievable requests.

# Solution
# Say there are n employees/requests, for each one, I branch by two decisions, meaning there are 2^n nodes. Each leaf node I spend n time solving the mask. The non leaf nodes also spend n time generating a new mask. Technically solving the mask takes n^2 time as well due to working with bits. I believe we could have a boolean array which is only mutated which has faster complexity but may be slower in practice. I think instead of the mask we could just modify the outgoing / ingoing differences and validate everything is 0, we could even keep a net sum variable to do O(1) validation.

class Solution:
    def maximumRequests(self, n: int, requests: List[List[int]]) -> int:
        bits = len(requests)

        # returns 0 if the mask is invalid
        def getAchievableRequests(mask):
            buildingDiffs = defaultdict(int) # maps building to new changes
            setBits = 0
            for offset in range(bits):
                bit = (mask >> offset) & 1
                if not bit:
                    continue
                setBits += 1
                fromB, toB = requests[offset]
                buildingDiffs[fromB] -= 1
                buildingDiffs[toB] += 1
            if any(buildingDiffs.values()):
                return 0
            return setBits


        def dfs(mask, i):
            # base case
            if i == len(requests):
                return getAchievableRequests(mask)

            # if we accept this persons request
            maskIfAccept = (mask) | (1 << i)

            ifAccept = dfs(maskIfAccept, i + 1)
            ifSkip = dfs(mask, i + 1)

            return max(ifAccept, ifSkip)

        return dfs(0, 0)