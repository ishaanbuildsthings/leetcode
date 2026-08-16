class Solution:
    def nearestDrone(self, drones: list[list[int]], target: list[int]) -> int:
        dist = inf
        res = None
        for i in range(len(drones)):
            # print('----')
            x1, y1, rangei = drones[i]

            SCORE = abs(x1 - target[0]) + abs(y1 - target[1])
            # print(f'{SCORE=}')
            # print(f'{rangei=}')
            if SCORE > rangei:
                # print('fail')
                continue
            if SCORE < dist:
                # print(f'good')
                dist = SCORE
                res = i
                # print(f'res now: {res}')

        if res is None:
            return -1

        return res