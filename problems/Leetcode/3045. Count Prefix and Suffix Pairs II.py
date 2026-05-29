MOD = 10**9 + 7
BASE = 911
basePow = [1]
for i in range(10**5 + 5):
    basePow.append((basePow[-1]*BASE) % MOD)
class H:
    def __init__(self, w):
        hashVal = 0

        self.pf = []
        for c in w:
            pos = ord(c) - ord('a') + 1
            hashVal *= BASE
            hashVal += pos
            hashVal %= MOD
            self.pf.append(hashVal)

        self.sf = [None] * len(w)
        hashVal = 0
        for i in range(len(w) - 1, -1, -1):
            c = w[i]
            pos = ord(c) - ord('a') + 1
            gain = pos * basePow[len(w) - i - 1]
            hashVal += gain
            hashVal %= MOD
            self.sf[i] = hashVal
    def getSf(self, sz):
        return self.sf[-sz]

    def getHash(self, l, r):
        full = self.pf[r]
        left = self.pf[l-1] if l else 0
        width = r - l + 1
        left = (left * basePow[width]) % MOD
        full -= left
        full %= MOD
        return full
    def getPf(self, sz):
        return self.pf[sz - 1]

class Solution:
    def countPrefixSuffixPairs(self, words: List[str]) -> int:
        hashes = [H(w) for w in words]
        res = 0
        c = Counter() # counts full hashes
        for i, w in enumerate(words):
            h = hashes[i]
            for pfSize in range(1, len(w) + 1):
                pfHash = h.getPf(pfSize)
                # pfHash = h.getHash(0, pfSize - 1)
                # suffHash = h.getHash(len(w) - pfSize, len(w) - 1)
                suffHash = h.getSf(pfSize)
                if pfHash == suffHash:
                    res += c[pfHash]
            c[h.pf[-1]] += 1
        return res

        
