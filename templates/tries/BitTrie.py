class BitTrie:
    """
    Binary trie over non-negative integers.
    All operations O(B) where B = number of bits.
    Sentinel: -1 returned when no valid result exists.
    """
    def __init__(self, bits, inserts):
        self.B = bits
        self.maxNodes = (bits + 1) * inserts + 1
        self.children = [[-1, -1] for _ in range(self.maxNodes)]
        self.passed = [0] * self.maxNodes
        self.nextNode = 1  # node 0 is root

    def _alive(self, nid):
        return nid != -1 and self.passed[nid] > 0

    def size(self):
        return self.passed[0]

    def add(self, x):
        idx = 0
        self.passed[0] += 1
        for b in range(self.B - 1, -1, -1):
            bit = (x >> b) & 1
            if self.children[idx][bit] == -1:
                self.children[idx][bit] = self.nextNode
                self.nextNode += 1
            idx = self.children[idx][bit]
            self.passed[idx] += 1

    def remove(self, x):
        idx = 0
        self.passed[0] -= 1
        for b in range(self.B - 1, -1, -1):
            bit = (x >> b) & 1
            idx = self.children[idx][bit]
            self.passed[idx] -= 1

    # max XOR of x against any number in trie. -1 if empty.
    def maxXor(self, x):
        if not self.size():
            return -1
        idx = 0
        res = 0
        for b in range(self.B - 1, -1, -1):
            bit = (x >> b) & 1
            want = bit ^ 1
            if self._alive(self.children[idx][want]):
                res |= (1 << b)
                idx = self.children[idx][want]
            else:
                idx = self.children[idx][bit]
        return res

    # min XOR of x against any number in trie. -1 if empty.
    def minXor(self, x):
        if not self.size():
            return -1
        idx = 0
        res = 0
        for b in range(self.B - 1, -1, -1):
            bit = (x >> b) & 1
            if self._alive(self.children[idx][bit]):
                idx = self.children[idx][bit]
            else:
                res |= (1 << b)
                idx = self.children[idx][bit ^ 1]
        return res

    # kth smallest XOR of x against numbers in trie (1-indexed). -1 if k > size.
    def kthSmallestXor(self, x, k):
        if k <= 0 or k > self.size():
            return -1
        idx = 0
        res = 0
        for b in range(self.B - 1, -1, -1):
            bit = (x >> b) & 1
            sameChild = self.children[idx][bit]
            sameCnt = self.passed[sameChild] if self._alive(sameChild) else 0
            if k <= sameCnt:
                idx = sameChild
            else:
                k -= sameCnt
                res |= (1 << b)
                idx = self.children[idx][bit ^ 1]
        return res

    # kth largest XOR of x against numbers in trie (1-indexed). -1 if k > size.
    def kthLargestXor(self, x, k):
        if k <= 0 or k > self.size():
            return -1
        idx = 0
        res = 0
        for b in range(self.B - 1, -1, -1):
            bit = (x >> b) & 1
            want = bit ^ 1
            wantChild = self.children[idx][want]
            wantCnt = self.passed[wantChild] if self._alive(wantChild) else 0
            if k <= wantCnt:
                res |= (1 << b)
                idx = wantChild
            else:
                k -= wantCnt
                idx = self.children[idx][bit]
        return res

    # count of numbers y in trie where (x ^ y) >= threshold
    def countXorGTE(self, x, threshold):
        if not self.size():
            return 0
        idx = 0
        res = 0
        for b in range(self.B - 1, -1, -1):
            vbit = (x >> b) & 1
            tbit = (threshold >> b) & 1
            if tbit == 0:
                exceedChild = self.children[idx][vbit ^ 1]
                if self._alive(exceedChild):
                    res += self.passed[exceedChild]
                tieChild = self.children[idx][vbit]
                if not self._alive(tieChild):
                    return res
                idx = tieChild
            else:
                needChild = self.children[idx][vbit ^ 1]
                if not self._alive(needChild):
                    return res
                idx = needChild
        res += self.passed[idx]
        return res

    # count of numbers y in trie where (x ^ y) > threshold
    def countXorGT(self, x, threshold):
        return self.countXorGTE(x, threshold + 1)

    # count of numbers y in trie where (x ^ y) <= threshold
    def countXorLTE(self, x, threshold):
        return self.size() - self.countXorGT(x, threshold)

    # count of numbers y in trie where (x ^ y) < threshold
    def countXorLT(self, x, threshold):
        return self.size() - self.countXorGTE(x, threshold)

    # count of numbers y in trie where lo <= (x ^ y) <= hi
    def countXorInRange(self, x, lo, hi):
        if lo > hi:
            return 0
        return self.countXorLTE(x, hi) - self.countXorLT(x, lo)

    # min XOR of x against y where (x ^ y) >= threshold. -1 if none.
    def minXorGTE(self, x, threshold):
        rank = self.countXorLT(x, threshold) + 1
        return self.kthSmallestXor(x, rank)  # -1 automatically if rank > size

    # max XOR of x against y where (x ^ y) <= threshold. -1 if none.
    def maxXorLTE(self, x, threshold):
        cnt = self.countXorLTE(x, threshold)
        if cnt == 0:
            return -1
        return self.kthLargestXor(x, self.size() - cnt + 1)