# not super optimized, and probably can do more things
class BitTrie:
    def __init__(self, BITS=32):
        self.BITS = BITS
        # Flatten nodes into arrays. Node 0 is root.
        # children[node][0] and children[node][1]
        self.children = [[-1, -1]]
        self.count = [0]
        self.nodeCount = 1

    def _newNode(self):
        self.children.append([-1, -1])
        self.count.append(0)
        idx = self.nodeCount
        self.nodeCount += 1
        return idx

    # Inserts a number into the Trie
    # O(BITS) time
    def insert(self, num):
        curr = 0
        for bitOffset in range(self.BITS - 1, -1, -1):
            bit = (num >> bitOffset) & 1
            if self.children[curr][bit] == -1:
                self.children[curr][bit] = self._newNode()
            self.count[curr] += 1
            curr = self.children[curr][bit]
        self.count[curr] += 1

    # Removes a number from the Trie (must have been inserted)
    # O(BITS) time
    def delete(self, num):
        curr = 0
        for bitOffset in range(self.BITS - 1, -1, -1):
            bit = (num >> bitOffset) & 1
            self.count[curr] -= 1
            curr = self.children[curr][bit]
        self.count[curr] -= 1

    # Counts numbers in Trie where (num XOR valToBeXord) >= threshold
    # O(BITS) time
    def countNumbersGTEVal(self, valToBeXord, threshold):
        curr = 0
        res = 0
        for bitOffset in range(self.BITS - 1, -1, -1):
            if curr == -1:
                break
            limitBit = (threshold >> bitOffset) & 1
            valueBit = (valToBeXord >> bitOffset) & 1
            xor0 = self.children[curr][valueBit]       # XOR result bit = 0
            xor1 = self.children[curr][1 - valueBit]   # XOR result bit = 1

            if limitBit == 0:
                # Take entire xor1 subtree (guaranteed >=), recurse into xor0
                if xor1 != -1:
                    res += self.count[xor1]
                curr = xor0
            else:
                # Skip xor0 subtree (guaranteed <), recurse into xor1
                curr = xor1

        # Exact match at leaf counts as >=
        if curr != -1:
            res += self.count[curr]
        return res