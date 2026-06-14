class Solution:
    def leastBricks(self, wall: List[List[int]]) -> int:
        rightEdgeToCount = defaultdict(int)
        for w in wall:
            rightEdge = 0
            for i, brick in enumerate(w):
                if i == len(w) - 1:
                    continue
                rightEdge += brick
                rightEdgeToCount[rightEdge] += 1
        return len(wall) - max(rightEdgeToCount.values()) if rightEdgeToCount else len(wall)