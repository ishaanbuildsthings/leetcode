class Solution:
    def minOperations(self, nums: List[int]) -> int:
        c = Counter(nums)
        countSingle = sum(v == 1 for v in c.values())
        ops = 0
        if countSingle == len(c):
            return 0

        for i in range(0, len(nums), 3):
            ops += 1            
            
            c[nums[i]] -= 1
            if c[nums[i]] == 1:
                countSingle += 1
            elif c[nums[i]] == 0:
                del c[nums[i]]
                countSingle -= 1

            if i + 1 < len(nums):
                c[nums[i + 1]] -= 1
                if c[nums[i+1]] == 1:
                    countSingle += 1
                elif c[nums[i+1]] == 0:
                    del c[nums[i+1]]
                    countSingle -= 1

            if i + 2 < len(nums):
                c[nums[i+2]] -= 1
                if c[nums[i+2]] == 1:
                    countSingle += 1
                elif c[nums[i+2]] == 0:
                    del c[nums[i+2]]
                    countSingle -= 1

            if countSingle == len(c):
                return ops
            
        return ops