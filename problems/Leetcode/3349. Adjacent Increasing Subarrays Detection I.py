class Solution:
    def hasIncreasingSubarrays(self, nums: List[int], k: int) -> bool:
        incs = set()
        for start in range(len(nums) - k + 1):
            failSeen = False
            for right in range(start + 1, start + k):
                if nums[right] <= nums[right - 1]:
                    failSeen = True
                    break
            if not failSeen:
                incs.add(start)
        
        
        for leftStart in range(len(nums)):
            rightStart = leftStart + k
            if leftStart in incs and rightStart in incs:
                return True
        
        return False