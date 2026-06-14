class Solution:
    def maxDistinctElements(self, nums: List[int], k: int) -> int:
        nums.sort()
        nums[0] -= k
        for i in range(1, len(nums)):
            prev = nums[i - 1]
            down = nums[i] - k
            up = nums[i] + k
            if prev < down:
                nums[i] = down
                continue
            if prev < up:
                nums[i] = prev + 1
                continue
            if prev >= up:
                nums[i] = up
        return len(set(nums))