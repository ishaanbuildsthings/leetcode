# https://leetcode.com/problems/the-most-similar-path-in-a-graph/description/
# Difficulty: Hard
# Tags: Dynamic Programming 2d

# Problem
# We have n cities and m bi-directional roads where roads[i] = [ai, bi] connects city ai with city bi. Each city has a name consisting of exactly three upper-case English letters given in the string array names. Starting at any city x, you can reach any city y where y != x (i.e., the cities and the roads are forming an undirected connected graph).

# You will be given a string array targetPath. You should find a path in the graph of the same length and with the minimum edit distance to targetPath.

# You need to return the order of the nodes in the path with the minimum edit distance. The path should be of the same length of targetPath and should be valid (i.e., there should be a direct road between ans[i] and ans[i + 1]). If there are multiple answers return any one of them.

# The edit distance is defined as follows:

# Solution, O(targetpath length * number of nodes * number of edges) time, O(targetpath length * number of nodes) space
# We can store a dp state of `i` which is the remaining targetpath we need to enumerate, and the current node we are at. This is targetpath length * number of nodes states. For each state, we may consider all neighbor nodes.

class Solution:
    def mostSimilar(self, n: int, roads: List[List[int]], names: List[str], targetPath: List[str]) -> List[int]:
        edges = defaultdict(list) # maps a node to a list of nodes it can reach
        for a, b in roads:
            edges[a].append(b)
            edges[b].append(a)

        # memo[i][current node] tells us the answer to the problem for the remaining path [i:] where we are situated at current node, it tells us both the path and the edit distance
        @cache
        def dp(i, currentNode):
            # base case
            if i == len(targetPath):
                return [[], 0]

            minEditDistanceForThis = float('inf')
            for adjNode in edges[currentNode]:
                pathForAdj, editDistanceForAdj = dp(i + 1, adjNode)
                if names[adjNode] != targetPath[i]:
                    editDistanceForAdj += 1
                if editDistanceForAdj < minEditDistanceForThis:
                    minEditDistanceForThis = editDistanceForAdj
                    bestPathForThis = [adjNode, *pathForAdj]

            return [bestPathForThis, minEditDistanceForThis]

        minEditDistance = float('inf')
        for node in range(n):
            pathStartingFromNode, minEditDistanceStartingFromNode = dp(0, node)
            if minEditDistanceStartingFromNode < minEditDistance:
                result = pathStartingFromNode
                minEditDistance = minEditDistanceStartingFromNode
        return result