class Solution:
    def findMinimumTime(self, strength: List[int], k: int) -> int:
        fullMask = (1 << len(strength)) - 1
        @cache
        def dp(maskBroken, x):
            # print(maskBroken,energy,x)
            if maskBroken == fullMask:
                return 0
            
            resHere = inf
            
            # allowed to wait if there is a lock with more cost than our current energy, but we dont have tooo much energy
            for i in range(len(strength)):
                if maskBroken >> i & 1:
                    continue
                lockStrength = strength[i]
                neededEnergy = lockStrength
                currGain = x
                waitsNeeded = math.ceil(neededEnergy/currGain)
                newMask = maskBroken | (1 << i)
                nextDp = waitsNeeded + dp(newMask, x + k)
                resHere = min(resHere, nextDp)
                    
            
            # if allowedWait:
            #     # print('allowed')
            #     resHere = dp(maskBroken, energy + x, x) + 1

            
            return resHere
        
        a = dp(0, 1)
        dp.cache_clear()
        return a
                