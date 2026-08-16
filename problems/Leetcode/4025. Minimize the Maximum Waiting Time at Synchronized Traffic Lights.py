class Solution:
    def minPenalty(self, period: int, lights: list[int], arrivalTime: list[int]) -> int:

        # a car gets at some time in the period
        # we get get to a light at a time=2 after a cycle and the light is green we go, otherwise we wait

        # for each car we need to find the optimal light to wait at


        mx = max(lights)
        res = 0

        for v in arrivalTime:
            remain = v % period
            # print(f'{remain=}')
            if remain < mx:
                # print(f'smaller than mx, just continuing')
                continue
            # print(f'have to wait: {period - remain}')
            res = max(res, period - remain)

        return res