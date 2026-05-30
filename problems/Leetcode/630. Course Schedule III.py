from sortedcontainers import SortedList
class Solution:
    def scheduleCourse(self, courses: List[List[int]]) -> int:
        # filter any courses that are impossible
        courses = [course for course in courses if course[0] <= course[1]]
        if not courses:
            return 0
        courses.sort(key = lambda c : c[1])
        # holds sizes
        sl = SortedList()
        sl.add(courses[0][0])
        totalSize = courses[0][0]

        for i in range(1, len(courses)):
            sz, lastDay = courses[i]
            if sz + totalSize <= lastDay:
                sl.add(sz)
                totalSize += sz
            else:
                big = sl[-1]
                if big > sz:
                    sl.pop(-1)
                    sl.add(sz)
                    totalSize -= big
                    totalSize += sz
        
        return len(sl)
        