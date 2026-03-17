class Solution:
    def allCellsDistOrder(self, rows: int, cols: int, rCenter: int, cCenter: int) -> List[List[int]]:
        # technically worse complexity than spiral matrix lol
        return sorted(([r, c] for r in range(rows) for c in range(cols)), key=lambda tup: abs(tup[0] - rCenter) + abs(tup[1] - cCenter))