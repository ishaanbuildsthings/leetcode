class Solution:
    def largestPower(self, nums: list[int]) -> list[int]:

        def solve(arr, andLeft, preserveBit):
            if len(arr) == 0:
                return []
            if len(arr) == 1:
                return arr[:]
            if preserveBit == -1:
                return arr[:]
            if not (1 << preserveBit) & andLeft:
                return solve(arr, andLeft, preserveBit - 1)

            withTopBit = [x for x in arr if x & (1 << preserveBit)]
            if not withTopBit:
                return solve(arr, andLeft, preserveBit - 1)

            withoutTopBit = [x for x in arr if not x & (1 << preserveBit)]

            lefty = solve(withTopBit, andLeft, preserveBit - 1)
            nandLeft = andLeft
            for v in withTopBit:
                nandLeft &= v

            righty = solve(withoutTopBit, nandLeft, preserveBit - 1)
            return lefty + righty

        sortedArr = solve(nums, (1 << 15) - 1, 14)
        res = [0] * 15
        for b in range(15):
            streak = 0
            for i, v in enumerate(sortedArr):
                if v & (1 << b):
                    streak += 1
                else:
                    break
            res[b] = streak

        return res[::-1]
                
            