class Solution:
    def maxSum(self, nums: List[int], k: int) -> int:
        # 1000
        # 0101
        # 0010
        # 0110


        # 1111
        # 0110
        bits = Counter()
        for num in nums:
            for b in range(32):
                if (1 << b) & num:
                    bits[b] += 1
        
        MOD = 10**9 + 7
        res = 0

        for _ in range(k):
            item = 0
            for bit in range(31, -1, -1):
                if bits[bit]:
                    bits[bit] -= 1
                    item |= (1 << bit)
            res += item**2
            res %= MOD
        
        return res
            