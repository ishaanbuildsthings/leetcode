class Solution:
    def isTrionic(self, nums: List[int]) -> bool:
        for i in range(1, len(nums)):
            for j in range(i + 1, len(nums) - 1):
                s1 = nums[:i+1]
                s2 = nums[i:j+1]
                s3 = nums[j:]

                if len(set(s1)) != len(s1):
                    continue
                if len(set(s2)) != len(s2):
                    continue
                if len(set(s3)) != len(s3):
                    continue
                if s1 != sorted(s1):
                    continue
                if s2 != sorted(s2, reverse=True):
                    continue
                if s3 != sorted(s3):
                    continue
                return True

        return False