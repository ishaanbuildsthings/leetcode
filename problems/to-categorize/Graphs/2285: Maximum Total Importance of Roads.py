# https://leetcode.com/problems/maximum-total-importance-of-roads/
# difficulty: medium
# tags: graph, greedy, functional

# Problem
# You are given an integer n denoting the number of cities in a country. The cities are numbered from 0 to n - 1.

# You are also given a 2D integer array roads where roads[i] = [ai, bi] denotes that there exists a bidirectional road connecting cities ai and bi.

# You need to assign each city with an integer value from 1 to n, where each value can only be used once. The importance of a road is then defined as the sum of the values of the two cities it connects.

# Return the maximum total importance of all roads possible after assigning the values optimally.

# Solution, O(E) time to get the frequency for how many times a node appears (and O(V) space), then we sort on O(V) and sum over O(V). Greedily select the biggest nodes first.

class Solution:
    def maximumImportance(self, n: int, roads: List[List[int]]) -> int:
        frqs = defaultdict(int)
        for a, b in roads:
            frqs[a] += 1
            frqs[b] += 1
        frqsArr = sorted(frqs.values(), reverse=True)
        return sum(
            frqsArr[i] * (n - i)
            if i < len(frqsArr)
            else 0
            for i in range(n)
        )

# 5*4
# 4*3
# 3*2
# 2*2
# 1*1
