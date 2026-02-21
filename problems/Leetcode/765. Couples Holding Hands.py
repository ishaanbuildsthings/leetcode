class Solution:
    def minSwapsCouples(self, row: List[int]) -> int:
        # 0 2 1 3 ...

        # 0 X          1 Y

        res = 0
        N = len(row)
        for i in range(0, N, 2):
            if abs(row[i] - row[i + 1]) == 1 and min(row[i], row[i + 1]) % 2 == 0:
                continue
            one = row[i]
            req = one ^ 1
            idx = row.index(req) # can be optimized to be O(1)
            res += 1
            row[i + 1], row[idx] = row[idx], row[i + 1]

        return res