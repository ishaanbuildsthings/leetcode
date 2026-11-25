# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/golden-references/TopoSortCourseSchedule.py
# Topological sort (Kahn's algorithm) as a full solution to LeetCode 207 "Course Schedule"
# (https://leetcode.com/problems/course-schedule/).
# Count each course's unfinished prerequisites. Courses with none are available; finishing one lowers the count of
# every course that needs it, and any course that hits 0 becomes available. If a cycle exists, its courses never hit
# 0, so fewer than numCourses get finished.
# Time O(V + E), space O(V + E).
from typing import List

class Solution:
    def canFinish(self, numCourses: int, prerequisites: List[List[int]]) -> bool:
        reqs = [0] * numCourses
        g = [[] for _ in range(numCourses)]
        for a, b in prerequisites:
            reqs[b] += 1
            g[a].append(b)
        
        avail = []
        for course in range(numCourses):
            if not reqs[course]: avail.append(course)
        
        finished = 0

        while avail:
            course = avail.pop()
            finished += 1
            for after in g[course]:
                reqs[after] -= 1
                if not reqs[after]:
                    avail.append(after)
        
        return finished == numCourses

