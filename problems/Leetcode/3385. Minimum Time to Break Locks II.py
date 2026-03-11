from scipy.optimize import linear_sum_assignment

def findOptimalAssignment(costMatrix):
    rowIndices, colIndices = linear_sum_assignment(costMatrix)
    return colIndices.tolist()

class Solution:
    def findMinimumTime(self, strength: List[int]) -> int:
        n = len(strength)
        costMatrix = [[0] * n for _ in range(n)]
        for position in range(n):
            gain = position + 1
            for sI in range(n):
                s = strength[sI]
                waitTime = ceil(s / gain)
                costMatrix[position][sI] = waitTime

        assignment = findOptimalAssignment(costMatrix)
        res = 0
        for i, lock in enumerate(assignment):
            gainPerMin = i + 1
            waitTime = ceil(strength[lock] / gainPerMin)
            res += waitTime
        return res

        
        # greedy that doesnt work
        # # 30, 40, 40, 45
        # # FAILS because when we have (40, 45) left and gain 3 per minute, we could wait 14 min and break 40, then 12 min and break 45 with our greedy, but optimally we wait 15 min and break 15, then 10 and break 40
        # remain = SortedList(strength)
        # gainPerMin = 1
        # res = 0
        # while remain:
        #     print(remain)
        #     first = remain[0]
        #     wait = ceil(first / gainPerMin)
        #     power = wait * gainPerMin
        #     print(f'power: {power}, wait: {wait}, gpm: {gainPerMin}')
        #     biggestLTEPower = findLargestLessThanOrEqual(remain, power)
        #     print(f'biggest lte: {biggestLTEPower}')
        #     res += wait
        #     gainPerMin += 1
        #     remain.remove(biggestLTEPower)
        # return res
            

        # weird dp idea that doesnt work
        # @cache
        # def dp(l, r, currentGainPerMinute):
        #     # base case
        #     if l > r:
        #         return 0
            
        #     minTimeHere = inf
        #     for i in range(l, r + 1):
        #         s = strength[i]
        #         waitTime = ceil(s / currentGainPerMinute)
        #         ifBreakHere = waitTime + dp(l, i - 1, currentGainPerMinute + 1) + dp(i + 1, r, currentGainPerMinute + 1)
        #         minTimeHere = min(minTimeHere, ifBreakHere)
            
        #     return minTimeHere
        
        # return dp(0, len(strength) - 1, 1)