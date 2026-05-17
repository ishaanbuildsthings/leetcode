class Solution:
    def countKthRoots(self, l: int, r: int, k: int) -> int:
        if k == 1:
            return r - l + 1
        res = set()
        UP = int(math.sqrt(r)) + 3
        # print(f'{UP=}')
        # for num in range(math.sqrt())
        for num in range(UP + 1):
            # big = num**k
            big = pow(num, k)
            if l <= big <= r:
                res.add(big)
            if big > r:
                break
        return len(res)
                