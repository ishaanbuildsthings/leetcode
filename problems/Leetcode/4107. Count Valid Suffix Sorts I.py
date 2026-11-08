class Solution:
    def countSuffix(self, nums: list[int], target: list[int]) -> int:
        longestPf = 0
        for i in range(len(nums)):
            if nums[i] == target[i]:
                longestPf += 1
            else:
                break
        
        res = 0
        
        vToRand = {}
        for v in nums + target:
            if v not in vToRand:
                rand = random.randint(1, 10**12)
                vToRand[v] = rand
        
        tot1 = 0
        tot2 = 0

        for i in range(len(nums) -1, -1, -1):
            if i < len(nums) - 1 and target[i] < target[i + 1]:
                break
            v = nums[i]
            t = target[i]
            tot1 += vToRand[v]
            tot2 += vToRand[t]
            if tot1 == tot2 and longestPf >= i:
                res += 1
        
        return res
