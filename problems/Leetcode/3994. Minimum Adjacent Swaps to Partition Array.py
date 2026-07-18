class Solution:
    def minAdjacentSwaps(self, nums: list[int], a: int, b: int) -> int:
        MOD = 10**9 + 7
        nums = [-1 if x < a else 0 if x <= b else 1 for x in nums]
        # print(nums)

        # each -1 takes i swaps minus the number of -1s before it
        swapsForNegOne = 0
        negOneCount = 0
        for i, v in enumerate(nums):
            if v != -1:
                continue
            swapsForNegOne += (i - negOneCount)
            negOneCount += 1

        # print(f'{swapsForNegOne=}')
        # print(f'{negOneCount=}')


        arr2 = []
        for v in nums:
            if v == -1:
                continue
            arr2.append(v)


        # print(f'{arr2=}')
        swapsForZero = 0
        zeroCount = 0
        for i, v in enumerate(arr2):
            if v != 0:
                continue
            swapsForZero += (i - zeroCount)
            zeroCount += 1

        # print(f'{swapsForZero=}')
        # print(f'{zeroCount=}')

        return (swapsForNegOne + swapsForZero) % MOD
            