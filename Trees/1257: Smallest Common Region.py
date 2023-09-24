# https://leetcode.com/problems/smallest-common-region/description/
# difficulty: medium
# tags: trees, lca

# Problem
# You are given some lists of regions where the first region of each list includes all other regions in that list.

# Naturally, if a region x contains another region y then x is bigger than y. Also, by definition, a region x contains itself.

# Given two regions: region1 and region2, return the smallest region that contains both of them.

# If you are given regions r1, r2, and r3 such that r1 includes r3, it is guaranteed there is no r2 such that r2 includes r3.

# It is guaranteed the smallest region exists.

# Solution, O(n) time and space
# For each region, populate its children. Then dfs down and bubble the info back up.

class Solution:
    def findSmallestRegion(self, regions: List[List[str]], region1: str, region2: str) -> str:
        children = defaultdict(list) # maps a node to its children
        for row in regions:
            for i in range(1, len(row)):
                children[row[0]].append(row[i])

        # returns if we have seen a, seen b, or if we have seen both, returns the lca
        def dfs(node):
            hasSeenA = node == region1
            hasSeenB = node == region2
            for child in children[node]:
                res = dfs(child)
                if isinstance(res, str):
                    return res
                childSeenA, childSeenB = res
                hasSeenA = hasSeenA or childSeenA
                hasSeenB = hasSeenB or childSeenB
            if hasSeenA and hasSeenB:
                return node
            return [hasSeenA, hasSeenB]
        return dfs(regions[0][0])
