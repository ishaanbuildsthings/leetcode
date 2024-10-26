# https://leetcode.com/problems/find-the-town-judge/description/?envType=daily-question&envId=2024-02-22
# difficulty: easy

# Problem
# In a town, there are n people labeled from 1 to n. There is a rumor that one of these people is secretly the town judge.

# If the town judge exists, then:

# The town judge trusts nobody.
# Everybody (except for the town judge) trusts the town judge.
# There is exactly one person that satisfies properties 1 and 2.
# You are given an array trust where trust[i] = [ai, bi] representing that the person labeled ai trusts the person labeled bi. If a trust relationship does not exist in trust array, then such a trust relationship does not exist.

# Return the label of the town judge if the town judge exists and can be identified, or return -1 otherwise.

# Solution
# O(n) time and space, can just use one hashmap

class Solution:
    def findJudge(self, n: int, trust: List[List[int]]) -> int:
        # can use just one hashmap which is # of people who trust you - # of people you trust
        trustedCounts = defaultdict(int)
        trustCounts = defaultdict(int)
        for a, b in trust:
            trustedCounts[b] += 1
            trustCounts[a] += 1
        for num in range(1, n + 1):
            if trustedCounts[num] == n - 1 and not trustCounts[num]:
                return num
        return -1