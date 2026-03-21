class Solution:
    def maxStudentsOnBench(self, students: List[List[int]]) -> int:
        bToS = defaultdict(set)
        for s, b in students:
            bToS[b].add(s)
        return max(list(len(x) for x in bToS.values()),default=0)