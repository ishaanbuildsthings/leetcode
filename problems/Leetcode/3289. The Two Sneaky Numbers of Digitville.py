class Solution:
    def getSneakyNumbers(self, nums: List[int]) -> List[int]:
        # c = Counter(nums)
        # res = []
        # for key in c:
        #     if c[key] == 2:
        #         res.append(key)
        # return res


        xor = 0
        for n in nums:
            xor ^= n
        for num in range(len(nums) - 2):
            xor ^= num
                
        msb = None
        for offset in range(32):
            if (xor >> offset) & 1:
                msb = offset
                break
        
        maskForNumsWithSetBit = xor
        maskForNumsWithoutSetBit = xor
        for n in range(len(nums) - 2):
            if (n >> msb) & 1:
                maskForNumsWithSetBit ^= n
            else:
                maskForNumsWithoutSetBit ^= n
        for n in nums:
            if (n >> msb) & 1:
                maskForNumsWithSetBit ^= n
            else:
                maskForNumsWithoutSetBit ^= n      
        
        return [maskForNumsWithSetBit, maskForNumsWithoutSetBit]