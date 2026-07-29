class Solution:
    def distanceBetweenBusStops(self, distance: List[int], start: int, destination: int) -> int:
        # can use fewer sums
        direct = sum(distance[i] for i in range(min(start, destination), max(start, destination)))
        tot = sum(distance)
        indirect = tot - direct
        return min(direct, indirect)