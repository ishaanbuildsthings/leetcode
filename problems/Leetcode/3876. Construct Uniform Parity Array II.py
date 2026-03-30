class Solution:
    def uniformArray(self, nums1: list[int]) -> bool:
        n = len(nums1)
        smallO = inf
        # smallE = inf
        for v in nums1:
            if v % 2 == 1:
                # smallE = min(smallE, v)
            # else:
                smallO = min(smallO, v)

        # print(f'{smallE=}, {smallO=}')


        # make all odd
        odds = [None] * n
        for i in range(n):
            if nums1[i] % 2:
                odds[i] = nums1[i]
                continue

            # we must subtract an odd number, smallest one
            if nums1[i] - smallO >= 1:
                odds[i] = nums1[i] - smallO


        if all(
            x is not None for x in odds
        ):
            # print(f'all odd')
            return True

        # make all even
        evens = [None] * n
        for i in range(n):
            if nums1[i] % 2 == 0:
                evens[i] = nums1[i]
                continue

            # must subtract odd
            if nums1[i] - smallO >= 1:
                evens[i] = nums1[i] - smallO

        if all(
            x is not None for x in evens
        ):
            # print(f'all even')
            return True

        return False