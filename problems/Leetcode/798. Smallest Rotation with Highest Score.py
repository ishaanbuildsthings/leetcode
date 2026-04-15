class Solution:
    def bestRotation(self, nums: List[int]) -> int:
        n = len(nums)
        sweep = [0] * (n + 1) # this is a sweep line on rotations

        def apply(l, r):
            sweep[l] += 1
            sweep[r + 1] -= 1

        for i, v in enumerate(nums):
            # so we score in indices v...n-1
            
            rotationsToPlaceToBack = i + 1
            diffWhenOnBack = (n - 1) - v # how many more rotations we can make
            maxRotations = rotationsToPlaceToBack + diffWhenOnBack
            # so now we have some range A...B of rotations that work
            # but B could be above N basically
            maxRotations %= n

            if rotationsToPlaceToBack <= maxRotations:
                apply(rotationsToPlaceToBack, maxRotations)
            else:
                apply(rotationsToPlaceToBack, n - 1)
                apply(0, maxRotations)
        

        curr = 0
        resMax = 0
        resI = None
        for i, v in enumerate(sweep):
            curr += v
            if curr > resMax:
                resMax = curr
                resI = i
            elif curr == resMax:
                if resI is None:
                    resI = i
                else:
                    resI = min(resI, i)
        return resI