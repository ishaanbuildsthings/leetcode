class Solution:
    def minRemovals(self, nums: List[int], target: int) -> int:

        
        if len(nums) == 1:
            if nums[0] == target:
                return 0
            if target == 0:
                return 1
            return -1
            
        n = len(nums)
        left = nums[:n//2]
        right = nums[n//2:]

        # print(f'{left=} {right=}')

        # minRemLeft = defaultdict(lambda: inf)

        def maker(arr):

            minRem = defaultdict(lambda: inf)

            for mask in range(1 << len(arr)):
                xor = 0
                removed = 0
                for i in range(len(arr)):
                    if mask & (1 << i):
                        xor ^= arr[i]
                    else:
                        removed += 1
                minRem[xor] = min(minRem[xor], removed)

            return minRem

        lefty = maker(left)
        righty = maker(right)

        # print(f'{lefty=}')

        res = inf

        for key in lefty:
            leftRemoves = lefty[key]
            rightReq = target ^ key
            rightRemoves = righty[rightReq]
            res = min(res, leftRemoves + rightRemoves)

        if res == inf:
            return -1

        return res