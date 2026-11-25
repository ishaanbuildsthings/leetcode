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

