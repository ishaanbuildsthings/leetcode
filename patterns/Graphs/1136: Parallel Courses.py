# https://leetcode.com/problems/parallel-courses/description/
# Difficulty: Medium
# Tags: Graphs, directed, topological sort, unconnected

# Problem
# You are given an integer n, which indicates that there are n courses labeled from 1 to n. You are also given an array relations where relations[i] = [prevCoursei, nextCoursei], representing a prerequisite relationship between course prevCoursei and course nextCoursei: course prevCoursei has to be taken before course nextCoursei.

# In one semester, you can take any number of courses as long as you have taken all the prerequisites in the previous semester for the courses you are taking.

# Return the minimum number of semesters needed to take all courses. If there is no way to take all the courses, return -1.

# Solution, O(V+E) time and space
# Before we can take a course, we must take its prereqs. The max time we need to take all courses is therefore bounded by the longest graph distance between a node and an eventual prereq. I.e. before we take calculus we must take pre-calc, geometry, algebra 2, algebra 1, etc. So for each node, dfs through its prereq chains getting the max distance. We cache the result for each node, so we solve at most every node once. We visit each edge once too.

class Solution:
    def minimumSemesters(self, n: int, relations: List[List[int]]) -> int:
        prereqs = defaultdict(list) # maps a node to a list of its prereqs
        for edge in relations:
            prevCourse, nextCourse = edge
            prereqs[nextCourse].append(prevCourse)

        path = set() # for cycle detection
        # given a node, searches its max prereq depth
        @cache
        def getMaxPrereqDepth(node):
            path.add(node)
            maxDepthForThis = 0
            for prereq in prereqs[node]:
                # have a cycle
                if prereq in path:
                    return -1
                depthForThisNode = 1 + getMaxPrereqDepth(prereq)
                # if the deeper node detected a path, continue that path detection
                if depthForThisNode == 0:
                    return - 1
                maxDepthForThis = max(maxDepthForThis, depthForThisNode)
            path.remove(node)
            return maxDepthForThis

        result = float('-inf')
        for node in range(1, n + 1):
            maxPrereqDepth = getMaxPrereqDepth(node)
            if maxPrereqDepth == -1:
                return -1
            result = max(result, maxPrereqDepth)
        return result + 1 # count courses not edges