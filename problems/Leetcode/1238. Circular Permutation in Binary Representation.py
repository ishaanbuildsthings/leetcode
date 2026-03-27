class Solution:
    def circularPermutation(self, n: int, start: int) -> List[int]:
        res = []
        for i in range(1 << n):
            res.append(i ^ (i >> 1))
        for i in range(len(res)):
            if res[i] == start:
                return res[i:] + res[:i]