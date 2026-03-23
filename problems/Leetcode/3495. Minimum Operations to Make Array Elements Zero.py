uppers = [] # upper boundaries mean we need i+1 operations to solve that
currPower = 1
skipNext = False
while True:
    if skipNext:
        break
    upper = 4**currPower
    if upper > 10**9:
        skipNext = True
    uppers.append(upper - 1)
    currPower += 1

class Solution:
    def minOperations(self, queries: List[List[int]]) -> int:
        # 1, 2, 3 -> 1 operation needed
        # 4, 5, 6, 7, ... 15 -> 2 operations needed
        # 16, ... 63 -> 3 operations needed
                
        def solveRange(low, high):
            c = Counter() # counts how many i+1ths we need for this range, for instance if we have 3 1s it means we have 3 things that take 2 operations
            for i in range(len(uppers)):
                upper = uppers[i]
                prev = uppers[i-1] if i > 0 else 0
                top = min(upper, high)
                bot = max(prev + 1, low)
                inRange = max(0, top - bot + 1)
                c[i] = inRange
            
            totalValues = high - low + 1
            
            opsUsed = 0
            for key in c:
                opsNeededHere = key + 1
                val = c[key]
                opsUsed += opsNeededHere * val
            return math.ceil(opsUsed / 2)
            
        
        ans = 0
        for low, high in queries:
            ans += solveRange(low, high)
        return ans
            
        