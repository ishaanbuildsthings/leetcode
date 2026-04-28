class Solution:
    def maxNumberOfFamilies(self, n: int, reservedSeats: List[List[int]]) -> int:
        rows = defaultdict(set)
        for row, col in reservedSeats:
            rows[row].add(col)
        res = 0
        for k in rows:
            row = rows[k]
            left = not any(x in row for x in [2, 3, 4, 5])
            right = not any(x in row for x in [6, 7, 8, 9])
            mid = not any(x in row for x in [4, 5, 6, 7])
            if left:
                res += 1
                if right:
                    res += 1
            else:
                if mid:
                    res += 1
                else:
                    if right:
                        res += 1
            
        fullRows = n - len(rows)
        res += fullRows * 2
        return res