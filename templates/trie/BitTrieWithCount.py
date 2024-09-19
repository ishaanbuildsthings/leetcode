# A bit trie class with a node class. Can insert numbersi into the trie, and count how many numbers, when XORd with a given number, are <= a threshold. O(BITS) time for both operations. Could add a remove number function, max XOR against a value, or min XOR against a value, functions. I think could also add max XOR of any two values in trie, or min XOR (some really good ICPC youtube video).

class Node:
    def __init__(self):
        self.countOfNumbers = 0 # the count of numbers in this nodes subtree
        self.children = {} # maps a 0 or 1 to a child Node
    def __str__(self, level=0):
        result = "  " * level + f"Node(count={self.countOfNumbers})\n"
        for bit, child in self.children.items():
            result += "  " * (level + 1) + f"Bit {bit}:\n"
            result += child.__str__(level + 2)
        return result

class BitTrie:
    def __init__(self, BITS=32):
        self.root = Node()
        self.BITS = BITS

    def __str__(self):
        return self.root.__str__()

    # Inserts a number into the Trie, O(BITS) time
    def insert(self, num):
        curr = self.root
        for bitOffset in range(self.BITS - 1, -1, -1):
            bit = (num >> bitOffset) & 1
            if bit not in curr.children:
                curr.children[bit] = Node()
            curr.countOfNumbers += 1
            curr = curr.children[bit]
        # add the count for the leaf node also
        curr.countOfNumbers += 1

    # Tells us how many numbers in the Trie, when XORd with `valToBeXord` are <= threshold, where threshold >= 0. O(BITS) time
    def countNumbersLTEVal(self, valToBeXord, threshold):
        if not self.root.children:
            return 0

        # Helper function that gets the answer for this sub problem
        def dfs(parentTrieNode, bitOffset):
            # Basically if we have a full match, so our number XORd with another number in the trie exactly equaled the threshold
            if bitOffset < 0:
                return parentTrieNode.countOfNumbers

            limitBit = (threshold >> bitOffset) & 1
            valueBit = (valToBeXord >> bitOffset) & 1

            resHere = 0

            # CASE 1: limit bit is 0, our value bit is 0, we recurse to 0 subtree
            if limitBit == 0 and valueBit == 0 and 0 in parentTrieNode.children:
                resHere += dfs(parentTrieNode.children[0], bitOffset - 1)

            # CASE 2: limit bit is 0, our value bit is 1, we recurse to 1 subtree
            if limitBit == 0 and valueBit == 1 and 1 in parentTrieNode.children:
                resHere += dfs(parentTrieNode.children[1], bitOffset - 1)

            # CASE 3: limit bit is 1, our value bit is 0, w can take the 0 subtree, and recurse to the 1 subtree
            if limitBit == 1 and valueBit == 0:
                if 0 in parentTrieNode.children:
                    resHere += parentTrieNode.children[0].countOfNumbers
                if 1 in parentTrieNode.children:
                    resHere += dfs(parentTrieNode.children[1], bitOffset - 1)

            # CASE 4: limit bit is 1, our value bit is 1, we can take the 1 subtree, and recurse to the 0 subtree
            if limitBit == 1 and valueBit == 1:
                if 1 in parentTrieNode.children:
                    resHere += parentTrieNode.children[1].countOfNumbers
                if 0 in parentTrieNode.children:
                    resHere += dfs(parentTrieNode.children[0], bitOffset - 1)

            return resHere

        return dfs(self.root, self.BITS - 1)