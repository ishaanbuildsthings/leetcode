class Solution:
    def rotate(self, nums: list[int], k: int) -> None:
        """
        Do not return anything, modify nums in-place instead.
        """
        # n = len(nums)
        # k = k % n
        # def reverse(l, r):
        #     while l < r:
        #         nums[l], nums[r] = nums[r], nums[l]
        #         l += 1
        #         r -= 1
        # reverse(0, n - 1)
        # reverse(0, k - 1)
        # reverse(k, n - 1)

        n = len(nums)
        k %= n
        if k == 0:
            return
        
        g = gcd(n, k)
        
        # every number is actually the number 3 to its left

        # rotates left by 1, at i, i-k, i-2k, ...
        def rotateBy1(i):
            start = nums[i]
            seenStart = False
            j = i
            while True:
                if j == i and seenStart:
                    break
                seenStart = True
                leftI = (j - k) % n
                if leftI == i:
                    onLeft = start
                else:
                    onLeft = nums[leftI]
                nums[j] = onLeft
                j = (j - k) % n
        
        for i in range(n - 1, n - 1 - g, -1):
            rotateBy1(i)