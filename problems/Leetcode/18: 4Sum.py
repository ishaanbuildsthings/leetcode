class Solution:
    def fourSum(self, nums: List[int], target: int) -> List[List[int]]:
        nums.sort()
        res = []
        for a in range(len(nums) - 3):
            # skip duplicate first numbers
            if a and nums[a] == nums[a - 1]:
                continue

            # do a 3sum on [b:]
            for b in range(a + 1, len(nums) - 2):

                # skip duplicate second numbers
                if b != a + 1 and nums[b] == nums[b - 1]:
                    continue

                threeSumTarget = target - nums[a]

                # do a two sum to reach threeSumTarget
                l = b + 1
                r = len(nums) - 1
                while l < r:
                    if l != b + 1 and nums[l] == nums[l - 1]:
                        l += 1
                        continue
                    
                    tot = nums[b] + nums[l] + nums[r]
                    if tot == threeSumTarget:
                        res.append([nums[a], nums[b], nums[l], nums[r]])
                        l += 1
                        continue
                    elif tot < threeSumTarget:
                        l += 1
                    else:
                        r -= 1
        
        return res
