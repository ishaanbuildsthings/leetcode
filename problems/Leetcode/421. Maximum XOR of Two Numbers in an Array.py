class BitTrie:
    def __init__(self, BITS):
        self.root = {}
        self.BITS = BITS
    
    def insert(self, num):
        curr = self.root
        for bitOffset in range(self.BITS - 1, -1, -1):
            bit = (num >> bitOffset) & 1
            if bit in curr:
                curr = curr[bit]
            else:
                newChild = {}
                curr[bit] = newChild
                curr = newChild
    
    def queryMaxXor(self, numToBeXord):
        res = 0
        curr = self.root
        for bitOffset in range(self.BITS - 1, -1, -1):
            numBit = (numToBeXord >> bitOffset) & 1
            desiredBit = numBit ^ 1

            if desiredBit in curr:
                res |= (1 << bitOffset)
                curr = curr[desiredBit]
            else:
                curr = curr[numBit]
        return res

    def queryMinXor(self, numToBeXord):
        res = 0
        curr = self.root
        for bitOffset in range(self.BITS - 1, -1, -1):
            numBit = (numToBeXord >> bitOffset) & 1

            if numBit in curr:
                curr = curr[numBit]
            else:
                res |= (1 << bitOffset)
                curr = curr[numBit ^ 1]
                
        return res


class Solution:
    def findMaximumXOR(self, nums: List[int]) -> int:
        big = max(nums)
        BITS = math.ceil(math.log2(big)) + 1 if big != 0 else 1
        t = BitTrie(BITS)
        for num in nums:
            t.insert(num)
        return max(map(t.queryMaxXor, nums))