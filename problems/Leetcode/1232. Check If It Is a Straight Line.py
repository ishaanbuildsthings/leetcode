class Solution:
    def checkStraightLine(self, coordinates: List[List[int]]) -> bool:
        def slope(p1, p2):
            if p1[0] == p2[0]:
                return inf
            return (p1[1] - p2[1]) / (p1[0] - p2[0])

        initSlope = slope(coordinates[0], coordinates[1])

        return all(
            slope(coordinates[0], coordinates[i]) == initSlope
            for i in range(1, len(coordinates))
        )