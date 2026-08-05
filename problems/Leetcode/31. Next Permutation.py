class Solution:
    def nextPermutation(self, nums: List[int]) -> None:
        """
        Do not return anything, modify nums in-place instead.
        """
        
        # 1 2 3 4 5 6
        # 9 8 7 6 5


        # desc -> "less" next perms
        # asc -> "more" next perms

        # find the beginning index of the monodecreasing portion
        monoStart = None

        for i in range(len(nums) - 1, -1, -1):
            if nums[i - 1] < nums[i]:
                monoStart = i
                break

        prev = -inf if not i else i - 1

        if prev == -inf:
            nums.reverse()
            return nums

        # find the rightmost number in the decreasing portion, > than prev
        rightmostBigger = None

        for i in range(len(nums) - 1, monoStart - 1, -1):
            if nums[i] > nums[prev]:
                rightmostBigger = i
                break
        
        nums[prev], nums[rightmostBigger] = nums[rightmostBigger], nums[prev]

        # can do O(1) space
        nums[prev + 1:] = nums[prev+1:][::-1]



        # for i in range(prev + 1, len(nums)):




        # 1 3 2


        # 3 1 2


        # 1 2 6 3

        # 1 3 2 6

        #   k      l
        # 3 5 (8 8 7 1)

        # swap 5 and 7

        # 3 7 (8 8 5 1)

        # 3 7 1 5 8 8




