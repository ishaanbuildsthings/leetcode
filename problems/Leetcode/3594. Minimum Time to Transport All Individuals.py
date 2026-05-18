from itertools import combinations
class Solution:
    def minTime(self, n: int, k: int, m: int, time: List[int], mul: List[float]) -> float:
        # fullmask = (1 << n) - 1

        # # dist[mask][currStage][side]

        # dist = [[[inf] * 2 for _ in range(m)] for _ in range(1<<n)]
        # dist[0][0][0] = 0
        # # print(f'{dist=}')


        # heap = [(0, 0, 0, 0)] # holds (cost, mask, stage, side)

        # # print(5 // 1)

        # while heap:
        #     cost, mask, stage, side = heapq.heappop(heap)
        #     # print(f'{cost=}, {mask=}, {stage=}, {side=}')
        #     if cost != dist[mask][stage][side]:
        #         continue
        #     if mask == fullmask and side == 1:
        #         return cost
        #     if side == 0:
        #         peopleOnLeft = [i for i in range(n) if ((mask >> i) & 1) == 0]
        #         for size in range(1, len(peopleOnLeft) + 1):
        #             if size > k:
        #                 break
        #             # generate all combos of people from peopleOnLeft
        #             for combo in combinations(peopleOnLeft, size):
        #                 slowTime = max(time[i] for i in combo)
        #                 totalTime = slowTime * mul[stage]
        #                 nextStage = stage + ((int(totalTime)) % m)
        #                 nextStage %= m
        #                 newMask = mask
        #                 for i in combo:
        #                     newMask |= (1 << i)
        #                 newCost = cost + totalTime
        #                 # prune
        #                 if newCost < dist[newMask][nextStage][side ^ 1]:
        #                     dist[newMask][nextStage][side ^ 1] = newCost
        #                     heapq.heappush(heap, (newCost, newMask, nextStage, side ^ 1))
        #     else:
        #         peopleOnRight = [i for i in range(n) if ((mask >> i) & 1)]
        #         # send one person back
        #         for person in peopleOnRight:
        #             totalTime = time[person] * mul[stage]
        #             nextStage = stage + ((int(totalTime)) % m)
        #             nextStage %= m
        #             newCost = cost + totalTime
        #             newMask = mask ^ (1 << person) # TODO
        #             if newCost < dist[newMask][nextStage][side ^ 1]:
        #                  dist[newMask][nextStage][side ^ 1] = newCost
        #                  heapq.heappush(heap, (newCost, newMask, nextStage, side ^ 1))


        # return -1

        fullMask = (1 << n) - 1

        @cache
        def maskToTime(mask):
            slowestTime = -inf
            for offset in range(n):
                if mask >> offset & 1:
                    slowestTime = max(slowestTime, time[offset])
            return slowestTime


        
        @cache
        def dp(maskLeft, stage, boatSide, singles):
            if singles >= 4:
                return inf
            maskRight = fullMask ^ maskLeft
            if maskRight == fullMask:
                return 0
            if boatSide == 0:
                resHere = inf
                submask = maskLeft
                while submask > 0:
                    if submask.bit_count() <= k:
                        if submask.bit_count() == 1:
                            newSingles = singles + 1
                        else:
                            newSingles = singles
                        slowTime = maskToTime(submask)
                        minutes = mul[stage] * slowTime
                        newMaskLeft = maskLeft ^ submask
                        newBoatSide = 1
                        newStage = (stage + (int(minutes) % m)) % m
                        dpHere = dp(newMaskLeft, newStage, newBoatSide, newSingles) + minutes
                        resHere = min(resHere, dpHere)
                    submask = (submask - 1) & maskLeft
                return resHere
            elif boatSide == 1:
                resHere = inf
                for offset in range(n):
                    if maskRight >> offset & 1:
                        timeForThisPerson = time[offset]
                        minutes = mul[stage] * timeForThisPerson
                        newMaskLeft = maskLeft | (1 << offset)
                        newStage = (stage + (int(minutes) % m)) % m
                        newBoatSide = 0
                        dpHere = dp(newMaskLeft, newStage, newBoatSide, singles) + minutes
                        resHere = min(resHere, dpHere)
                return resHere
        
        ans = dp(fullMask, 0, 0, 0)
        return ans if ans != inf else -1
