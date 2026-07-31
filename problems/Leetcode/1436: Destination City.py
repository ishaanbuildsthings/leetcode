# https://leetcode.com/problems/destination-city/description/?envType=daily-question&envId=2023-12-15
# difficulty: easy

# Problem
# You are given the array paths, where paths[i] = [cityAi, cityBi] means there exists a direct path going from cityAi to cityBi. Return the destination city, that is, the city without any path outgoing to another city.

# It is guaranteed that the graph of paths forms a line without any loop, therefore, there will be exactly one destination city.

# Solution, O(n) time and space
class Solution:
    def destCity(self, paths: List[List[str]]) -> str:
        seen = set(tup[1] for tup in paths)
        for path in paths:
            seen.discard(path[0])
        return list(seen)[0]

