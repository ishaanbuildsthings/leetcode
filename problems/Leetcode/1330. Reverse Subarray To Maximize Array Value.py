class Solution:
    def maxValueAfterReverse(self, nums: List[int]) -> int:
        
        # when we reverse L...R
        # then this happens:

        # we lose |A[L-1]-A[L]| and gain |A[L-1]-A[R]|
        # we lose |A[R]-A[R+1]| and gain |A[L]-A[R+1]|

        # call A=nums[L-1], B=nums[L], C=nums[R], D=nums[R+1]

        # delta = |A-C| + |B-D| - |A-B| - |C-D|

        # |A-B| and |C-D| are easy to compute, when we make our selections for A and C we can compute those

        # |A-C| and |B-D| are harder to compute, they are also independent
        # |A-C| = max(A-C, C-A)

        # we can treat |A-C| + |B-D| as
        # max(s1 * (A-C) + s2 * (B - D))
        # where s1 and s2 are signs in [-1, 1]

        maxDelta = 0

        for signPair in [[-1,-1],[-1,1],[1,1],[1,-1]]:
            s1, s2 = signPair

            pickedA = -inf # best score so far if we picked the A<>B cut point
            pickedBoth = -inf # best score if we have picked both
            for i in range(len(nums) - 1):
                num = nums[i]
                nxt = nums[i+1]

                # treat this num as A
                npickA = s1 * num + s2 * nxt - abs(num - nxt)

                # treat this num as C
                npickBoth = pickedA + (-s1 * num) + (-s2 * nxt) - abs(num - nxt)

                pickedA = max(pickedA, npickA)
                pickedBoth = max(pickedBoth, npickBoth)
            
            maxDelta = max(maxDelta, pickedBoth)
        
        # edge case 1, we reverse a prefix
        for i in range(len(nums) - 1):
            num = nums[i]
            nxt = nums[i+1]
            lost = abs(num - nxt)
            gain = abs(nxt - nums[0])
            maxDelta = max(maxDelta, gain - lost)
        
        # edge case 2, reverse suffix
        for i in range(len(nums) - 1, 0, -1):
            num = nums[i]
            prev = nums[i-1]
            lost = abs(num - prev)
            gain = abs(prev - nums[-1])
            maxDelta = max(maxDelta, gain - lost)
        
        normal = sum(abs(nums[i]-nums[i+1]) for i in range(len(nums) - 1))
        return normal + maxDelta