# https://leetcode.com/problems/minimum-amount-of-time-to-collect-garbage/description/?envType=daily-question&envId=2023-11-20
# difficulty: medium

# Problem
# You are given a 0-indexed array of strings garbage where garbage[i] represents the assortment of garbage at the ith house. garbage[i] consists only of the characters 'M', 'P' and 'G' representing one unit of metal, paper and glass garbage respectively. Picking up one unit of any type of garbage takes 1 minute.

# You are also given a 0-indexed integer array travel where travel[i] is the number of minutes needed to go from house i to house i + 1.

# There are three garbage trucks in the city, each responsible for picking up one type of garbage. Each garbage truck starts at house 0 and must visit each house in order; however, they do not need to visit every house.

# Only one garbage truck may be used at any given moment. While one truck is driving or picking up garbage, the other two trucks cannot do anything.

# Return the minimum number of minutes needed to pick up all the garbage.

# Solution, just iterate, we include travel as long as that truck sees more trash of its type. Time is total chars + len(garbage), space is O(1).

class Solution:
    def garbageCollection(self, garbage: List[str], travel: List[int]) -> int:
        gCost, pCost, mCost = 0, 0, 0
        gStreak, pStreak, mStreak = 0, 0, 0

        for i in range(len(garbage)):
            counts = collections.Counter(garbage[i])
            if counts['G']:
                gCost += (counts['G'] + gStreak)
                gStreak = 0
            if counts['P']:
                pCost += (counts['P'] + pStreak)
                pStreak = 0
            if counts['M']:
                mCost += (counts['M'] + mStreak)
                mStreak = 0
            if i < len(garbage) - 1:
                gStreak += travel[i]
                pStreak += travel[i]
                mStreak += travel[i]
        return gCost + pCost + mCost



