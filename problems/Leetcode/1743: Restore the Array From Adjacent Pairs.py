# https://leetcode.com/problems/restore-the-array-from-adjacent-pairs/description/?envType=daily-question&envId=2023-11-10
# difficulty: medium
# tags: dfs, graph, connected, undirected

# Problem
# There is an integer array nums that consists of n unique elements, but you have forgotten it. However, you do remember every pair of adjacent elements in nums.

# You are given a 2D integer array adjacentPairs of size n - 1 where each adjacentPairs[i] = [ui, vi] indicates that the elements ui and vi are adjacent in nums.

# It is guaranteed that every adjacent pair of elements nums[i] and nums[i+1] will exist in adjacentPairs, either as [nums[i], nums[i+1]] or [nums[i+1], nums[i]]. The pairs can appear in any order.

# Return the original array nums. If there are multiple solutions, return any of them.

# Solution, O(n) time and space
# We can find one of the two edges, then DFS through adjacent paths. There are many ways to do this (a seen set, tracking the previous number, using buckets which I did which is a little inefficient, etc). We can also just use an iterative while loop with a prev variable.

class Solution:
    def restoreArray(self, adjacentPairs: List[List[int]]) -> List[int]:
        edgeMap = defaultdict(set)
        counts = defaultdict(int)
        for a, b in adjacentPairs:
            edgeMap[a].add(b)
            edgeMap[b].add(a)
            counts[a] += 1
            counts[b] += 1
        for key in counts:
            if counts[key] == 1:
                start = key
                break

        res = []

        def dfs(num):
            res.append(num)
            nextEdgeBucket = list(edgeMap[num])
            if len(nextEdgeBucket) == 0:
                return
            nextEdgeNum = nextEdgeBucket[0]
            edgeMap[nextEdgeNum].remove(num)
            dfs(nextEdgeNum)


        dfs(start)

        return res



