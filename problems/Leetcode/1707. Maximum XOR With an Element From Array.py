class BitTrie:
    def __init__(self, BITS=32):
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
    
    # Returns the max XOR or None if there's no elements in Trie, O(BITS) time
    def queryMaxXor(self, numToBeXord):
        res = 0
        curr = self.root
        if not curr:
            return None
        for bitOffset in range(32 - 1, -1, -1):
            numBit = (numToBeXord >> bitOffset) & 1
            desiredBit = numBit ^ 1

            if desiredBit in curr:
                res |= (1 << bitOffset)
                curr = curr[desiredBit]
            else:
                curr = curr[numBit]
        return res

    # Returns the min XOR or None if there's no elements in Trie, O(BITS) time
    def queryMinXor(self, numToBeXord):
        res = 0
        curr = self.root
        if not curr:
            return None
        for bitOffset in range(self.BITS - 1, -1, -1):
            numBit = (numToBeXord >> bitOffset) & 1

            if numBit in curr:
                curr = curr[numBit]
            else:
                res |= (1 << bitOffset)
                curr = curr[numBit ^ 1]
                
        return res


class Solution:
    def maximizeXor(self, nums: List[int], queries: List[List[int]]) -> List[int]:
        nums.sort()
        newQueries = queries[::]
        newQueries.sort(key=lambda tup: (tup[1]))
        queriesToAnswer = {} # maps tup to answer

        t = BitTrie()

        r = 0 # the right edge, we will add elements from nums while we don't exceed the threshold
        for i in range(len(newQueries)):
            num, allowedUpTo = newQueries[i]
            while r < len(nums) and nums[r] <= allowedUpTo:
                t.insert(nums[r])
                r += 1
            biggestXor = t.queryMaxXor(num)
            queriesToAnswer[(num, allowedUpTo)] = biggestXor if biggestXor is not None else -1
        
        res = []
        for num, biggestAllowedUpTo in queries:
            res.append(queriesToAnswer[(num), biggestAllowedUpTo])
        return res













