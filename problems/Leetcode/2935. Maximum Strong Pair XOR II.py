    class BitTrie:
    def __init__(self, BITS=32):
        self.root = {}
        self.BITS = BITS

    def insert(self, num):
        curr = self.root
        for bitOffset in range(self.BITS - 1, -1, -1):
            bit = (num >> bitOffset) & 1
            if bit not in curr:
                curr[bit] = {}
            curr = curr[bit]
    
    def queryMaxXor(self, numToBeXord):
        res = 0
        curr = self.root
        if not curr:
            return None
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

    def remove(self, num):
        curr = self.root
        stack = []

        # Traverse and store the nodes and bits in a stack
        for bitOffset in range(self.BITS - 1, -1, -1):
            bit = (num >> bitOffset) & 1
            if bit not in curr:
                return  # The number doesn't exist in the trie
            stack.append((curr, bit))
            curr = curr[bit]

        # Remove nodes starting from the leaf
        while stack:
            node, bit = stack.pop()
            del node[bit]
            if node:
                break  # Stop if the current node has other children


class Solution:
    def maximumStrongPairXor(self, nums: List[int]) -> int:
        nums = list(set(nums)) # remove duplicates
        
        # forces length 21
        def toStr(num):
            # print(f'to str called on num {num}, str is: {bin(num)[2:].zfill(21)}')
            return bin(num)[2:].zfill(21)
        
        nums.sort()
        trie = BitTrie(32)
        trie.insert(nums[0])
        
        res = 0
        l = 0 # a pointer to our smallest number, we increment as needed
        
        for i in range(1, len(nums)):
            newNum = nums[i]
            while nums[l] < newNum / 2:
                lostNum = nums[l]
                lostNumStr = toStr(lostNum)
                trie.remove(lostNum)
                l += 1
                
                
            newNumStr = toStr(newNum)
            trie.insert(newNum)
            biggestCounterpart = trie.queryMaxXor(newNum)
            res = max(res, biggestCounterpart)
            
        
        return res
        