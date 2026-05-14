# https://leetcode.com/problems/course-schedule-iv/description/
# difficulty: medium
# tags: graphs, matrix dfs, matrix bfs, floyd warshall

# Problem
# There are a total of numCourses courses you have to take, labeled from 0 to numCourses - 1. You are given an array prerequisites where prerequisites[i] = [ai, bi] indicates that you must take course ai first if you want to take course bi.

# For example, the pair [0, 1] indicates that you have to take course 0 before you can take course 1.
# Prerequisites can also be indirect. If course a is a prerequisite of course b, and course b is a prerequisite of course c, then course a is a prerequisite of course c.

# You are also given an array queries where queries[j] = [uj, vj]. For the jth query, you should answer whether course uj is a prerequisite of course vj or not.

# Return a boolean array answer, where answer[j] is the answer to the jth query.

# Solution 1
# Floyd warshall, compute distance from any two nodes, treat an edge as a weight of 1. Floyd warshall will take V^3 + q time.

class Solution:
    def checkIfPrerequisite(self, n: int, prerequisites: List[List[int]], queries: List[List[int]]) -> List[bool]:
        prereqs = [[False] * n for _ in range(n)]
        for a, b in prerequisites:
            prereqs[a][b] = True

        # update prereqs with floyd warshall

        for k in range(n):
            for i in range(n):
                for j in range(n):
                    prereqs[i][j] = prereqs[i][j] or (prereqs[i][k] and prereqs[k][j])

        return [prereqs[i][j] for i, j in queries]


# * Solution 2
# BFS on each query, see if we reach the target. For a single query, we might iterate through all nodes and edges, so V+E. I think time complexity would then be queries * (V + E). And edges can be up to V^2 so maybe q*V^2. We can also do DFS, it's the same complexity, but BFS is bounded by the actual distance to the target node. We might be able to do some caching stuff with DFS too.

class Solution:
    def checkIfPrerequisite(self, n: int, prerequisites: List[List[int]], queries: List[List[int]]) -> List[bool]:
        edgeMap = defaultdict(list)
        for pre, post in prerequisites:
            edgeMap[pre].append(post)

        def solveQuery(start, end):
            q = collections.deque()
            q.append(start)
            seen = set()
            seen.add(start)
            while q:
                length = len(q)
                for _ in range(length):
                    popped = q.popleft()
                    for adj in edgeMap[popped]:
                        if adj in seen:
                            continue
                        if adj == end:
                            return True
                        seen.add(adj)
                        q.append(adj)
            return False

        return [solveQuery(queries[i][0], queries[i][1]) for i in range(len(queries))]

