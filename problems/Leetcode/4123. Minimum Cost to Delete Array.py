class Solution:
    def minCost(self, nums: list[int]) -> int:
        n = len(nums)
        if n == 2:
            return sum(nums)
        if n == 3:
            return nums[0] + nums[-1]

        inside = nums[1:-1]
        inside.sort()
        print(f'{inside=}')

        running = 0

        for i in range(0, len(inside), 2):
            if i == len(inside) - 1:
                break
            a = inside[i]
            b = inside[i+1]
            tot = a + b
            if tot < 0:
                running += tot
            else:
                break

        return nums[0] + nums[-1] + running
            