class Solution:
    def generate(self, numRows: int) -> List[List[int]]:
        row = [1]
        res = [row]
        for _ in range(numRows - 1):
            nrow = [1]
            for i in range(len(res[-1]) - 1):
                v1 = res[-1][i]
                v2 = res[-1][i+1]
                nv = v1 + v2
                nrow.append(nv)
            nrow.append(1)
            res.append(nrow)
        return res

