class Solution:
    def totalHammingDistance(self, nums: List[int]) -> int:
        B = 32
        countOnes = [0] * 32 # how many numbers have that bit set
        for b in range(B):
            for num in nums:
                if (1 << b) & num:
                    countOnes[b] += 1
        res = 0
        for b in range(B):
            ones = countOnes[b]
            zeroes = len(nums) - ones
            crossPairs = ones * zeroes
            res += crossPairs
        
        return res