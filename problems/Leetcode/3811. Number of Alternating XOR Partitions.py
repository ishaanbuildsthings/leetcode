class Solution:
    def alternatingXOR(self, nums: List[int], target1: int, target2: int) -> int:
        MOD = 10**9 + 7
        endA = defaultdict(int) # of ways to end with a block of target1 where the prefix xor is X in endA[X], ending at some index before our current element
        endB = defaultdict(int)
        endB[0] = 1
        
        pf = 0

        for i, v in enumerate(nums):
            pf ^= v
            reqToMakeT1 = pf ^ target1 # we need to cut off some suffix ending at i where the suffix is exactly target1 or target2
            # this corresponds to finding how many prefixes have reqToMakeT1 and already ended
            reqToMakeT2 = pf ^ target2

            addOne = endA[reqToMakeT2]
            addTwo = endB[reqToMakeT1]
            endB[pf] += addOne
            endA[pf] += addTwo

        return (addOne + addTwo) % MOD

