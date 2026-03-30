class Solution:
    def uniformArray(self, nums1: list[int]) -> bool:
        n = len(nums1)
        oddFail = False
        anyOdd = any(x % 2 == 1 for x in nums1)
        print(f'{anyOdd=}')
        for i in range(n):
            if nums1[i] % 2:
                continue
            if anyOdd:
                continue
            oddFail = True

        if not oddFail:
            return True


        evenFail = False
        for i in range(n):
            if nums1[i] % 2 == 0:
                continue
            # we are odd, must subtract odd
            if anyOdd:
                continue
            evenFail = True

        if not evenFail:
            return True

        return False