# A BitTrie with no node class. Just stores nested dictionaries indicating the presence of a bit at that position. Can get max XOR against a number, min XOR against a number, insert a number, and remove a number. I think could also add max XOR of any two values in trie, or min XOR (some really good ICPC youtube video).

class BitTrie:
    def __init__(self, BITS=32):
        self.root = {}
        self.BITS = BITS

    # Inserts a number into the Trie, O(BITS) time
    def insert(self, num):
        curr = self.root
        for bitOffset in range(self.BITS - 1, -1, -1):
            bit = (num >> bitOffset) & 1
            if bit not in curr:
                curr[bit] = {}
            curr = curr[bit]

    # Returns maxXor or None (if no elements in Trie), O(BITS) time
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

    # Returns minXor or None (if no elements in Trie), O(BITS) time
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

    # Returns if the number was removed, O(BITS) time
    def remove(self, num):
        curr = self.root
        stack = []

        for bitOffset in range(self.BITS - 1, -1, -1):
            bit = (num >> bitOffset) & 1
            if bit not in curr:
                return False
            stack.append((curr, bit))
            curr = curr[bit]

        while stack:
            node, bit = stack.pop()
            del node[bit]
            if node:
                break

        return True
