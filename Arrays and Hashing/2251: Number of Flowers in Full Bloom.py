# https://leetcode.com/problems/number-of-flowers-in-full-bloom/description/?envType=daily-question&envId=2023-10-11
# difficulty: hard
# tags: sweep line

# Problem
# You are given a 0-indexed 2D integer array flowers, where flowers[i] = [starti, endi] means the ith flower will be in full bloom from starti to endi (inclusive). You are also given a 0-indexed integer array people of size n, where people[i] is the time that the ith person will arrive to see the flowers.

# Return an integer array answer of size n, where answer[i] is the number of flowers that are in full bloom when the ith person arrives.

# Solution, O(n log n) time, O(n) space
# The range where flowers can exist is too wide to create a true sweep line. Instead, we just make a sweep line representing the critical moments where the number of flowers change. Then, we can create a prefix sweep to tell us the number of flowers in some range. Then we binary search on that prefix sweep to answer a query.
# I think this can be done with a single sweep line. Just iterate over the ranges, and construct the prefix sweep in one go.

class Solution:
    def fullBloomFlowers(self, flowers: List[List[int]], people: List[int]) -> List[int]:
        sweepMap = defaultdict(int) # maps a pos to a diff
        for l, r in flowers:
            sweepMap[l] += 1
            sweepMap[r+1] -=1
        sweep = [] # holds [pos, diff]
        for pos in sweepMap.keys():
            diff = sweepMap[pos]
            sweep.append([pos, diff])
        sweep.sort()

        prefixMap = defaultdict(int) # maps a prefix amount of steps at a critical moment to the number of flowers
        runningFlowers = 0
        for pos, diff in sweep:
            runningFlowers += diff
            prefixMap[pos] = runningFlowers

        prefix = [] # holds [pos, total acrrued]
        for pos in prefixMap:
            totalAccrued = prefixMap[pos]
            prefix.append([pos, totalAccrued])
        prefix.sort()
        positions = [tup[0] for tup in prefix] # helps bisect

        res = []
        for personPosition in people:
            index = bisect.bisect_right(positions, personPosition) # index where we would inser to maintain sorted
            lastSmallerPosition = index - 1
            flowerAmount = prefix[lastSmallerPosition][1]
            res.append(flowerAmount)
        return res


