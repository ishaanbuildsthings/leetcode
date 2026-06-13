class Solution:
    def minDeletion(self, nums: List[int]) -> int:
        deletes = 0
        arr = []
        i = 0
        while i < len(nums):
            v = nums[i]
            arr.append(v)
            j = i + 1
            for j in range(i + 1, len(nums)):
                if nums[j] == v:
                    deletes += 1
                    continue
                arr.append(nums[j])
                break
            i = j + 1
        if len(arr) % 2:
            deletes += 1
        return deletes
