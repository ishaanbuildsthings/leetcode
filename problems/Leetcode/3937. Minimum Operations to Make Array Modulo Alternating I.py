class Solution:
    def minOperations(self, nums: list[int], k: int) -> int:
        res = inf

        for x in range(k):
        # for x in ([1]):
            for y in range(k):
                if x == y:
                    continue
            # for y in ([2]):
                # print('========================')
                # print(f'{x=} {y=}')
                resHere = 0
                for i, v in enumerate(nums):
                    # print('========')
                    if i % 2 == 0:
                        # print(f'even index, need remainder of {x} at value={v}')
                        # v needs to have a remainder of X when divided by k
                        rem = v % k
                        # print(f'current rem is: {rem}')
                        d1 = max(rem, x) - min(rem, x)
                        d2 = (k - max(rem, x)) + min(rem, x)
                        dist = min(d1, d2)
                        # print(f'min dist was: {dist}')
                        resHere += dist
                    else:
                        # print(f'odd index, need remainder of {y} at value={v}')
                        rem = v % k
                        # print(f'current rem is: {rem}')
                        d1 = max(rem, y) - min(rem, y)
                        d2 = (k - max(rem, y)) + min(rem, y)
                        dist = min(d1, d2)
                        # print(f'min dist was: {dist}')
                        resHere += dist
                
                res = min(res, resHere)
                # print(f'res now: {res}')

        return res
                        