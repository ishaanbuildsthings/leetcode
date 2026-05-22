class Solution:
    def decode(self, encoded: List[int]) -> List[int]:
        n = len(encoded) + 1
        xorAll = 0
        for v in range(1, n + 1):
            xorAll ^= v
        
        # encoded[0] = A ^ B
        # encoded[2] = C ^ D
        # ...
        allEncoded = 0
        for i in range(0, len(encoded), 2):
            allEncoded ^= encoded[i]
        
        lastTerm = xorAll ^ allEncoded

        res = [None] * n
        res[-1] = lastTerm
        for i in range(n - 2, -1, -1):
            nxt = res[i + 1]
            nval = nxt ^ encoded[i]
            res[i] = nval
        
        return res
            
