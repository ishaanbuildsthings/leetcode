# https://leetcode.com/problems/maximum-coins-heroes-can-collect/
# difficulty: medium
# tags: sorting, binary search, prefix

# Problem
# There is a battle and n heroes are trying to defeat m monsters. You are given two 1-indexed arrays of positive integers heroes and monsters of length n and m, respectively. heroes[i] is the power of ith hero, and monsters[i] is the power of ith monster.

# The ith hero can defeat the jth monster if monsters[j] <= heroes[i].

# You are also given a 1-indexed array coins of length m consisting of positive integers. coins[i] is the number of coins that each hero earns after defeating the ith monster.

# Return an array ans of length n where ans[i] is the maximum number of coins that the ith hero can collect from this battle.

# Notes

# The health of a hero doesn't get reduced after defeating a monster.
# Multiple heroes can defeat a monster, but each monster can be defeated by a given hero only once.

# Solution, O(n log n) time and O(sort) space
# First, sort the monsters by increasing power, zip the indices or coins so we can access that. Then binary search for each hero to see the biggest one we can beat, and gain the prefix coin amount.

class Solution:
    def maximumCoins(self, heroes: List[int], monsters: List[int], coins: List[int]) -> List[int]:

        monsterMaxes = defaultdict(int)
        for i in range(len(monsters)):
            monsterMaxes[monsters[i]] = max(monsterMaxes[monsters[i]], coins[i])

        zipped = []
        for i in range(len(monsters)):
            tup = [monsters[i], coins[i]]
            zipped.append(tup)
        zipped.sort()

        prefixSums = []
        runningSum = 0
        for i in range(len(zipped)):
            coin = zipped[i][1]
            runningSum += coin
            prefixSums.append(runningSum)

        res = []
        for i in range(len(heroes)):
            hero = heroes[i]
            l = 0
            r = len(monsters) - 1
            while l <= r:
                m = (r + l) // 2
                monster = zipped[m][0]
                if monster > hero:
                    r = m - 1
                else:
                    l = m + 1
            if r == -1:
                res.append(0)
            else:
                res.append(prefixSums[r])
        return res