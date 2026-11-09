MOD = 10**9 + 7
B = 27
class Solution:
    def lexSmallest(self, s: str) -> str:
        n = len(s)
        
        r = s[::-1]

        shash = []
        curr = 0
        for v in s:
            curr *= B
            curr += ord(v) - ord('a')
            curr %= MOD
            shash.append(curr)
        
        rhash = []
        curr = 0
        for v in r:
            curr *= B
            curr += ord(v) - ord('a')
            curr %= MOD
            rhash.append(curr)


        # 1 2 |3 4| 5 6 7

        # take hash of 1234
        # subtract hash of 1200
        # take hash of 12 and scale up by width

        basePow = [1]
        for power in range(len(s)):
            basePow.append((basePow[-1] * B) % MOD)
        
        def hashRange(pf, l, r):
            if l > r: return 0
            big = pf[r]
            lost = pf[l - 1] if l else 0
            lost = (lost * basePow[r - l + 1]) % MOD
            return (big - lost) % MOD
        
        def combine(hash1, hash2, len2):
            big = (hash1 * basePow[len2]) % MOD
            return (big + hash2) % MOD
        
        # hash of 0...i with l...r reversed
        def hashPf(i, l, r):
            if i < l:
                return hashRange(shash, 0, i)
            
            hash1 = hashRange(shash, 0, l - 1)

            # i is inside l...r, positions l...i read s[r], s[r-1], ... which is forward in rhash from n-1-r
            if i <= r:
                width = i - l + 1
                hash2 = hashRange(rhash, n - 1 - r, n - 1 - r + width - 1)
                return combine(hash1, hash2, width)
            
            # i is past r, full reversed piece, then s continues from r+1
            hash2 = hashRange(rhash, n - 1 - r, n - 1 - l)
            hash12 = combine(hash1, hash2, r - l + 1)
            hash3 = hashRange(shash, r + 1, i)
            return combine(hash12, hash3, i - r)

        best = (0, 0) # i...j is reversed

        def charAt(idx, l, r):
            if l <= idx <= r:
                return s[l + r - idx]
            return s[idx]

        cands = []
        for i in range(len(s)):
            cands.append((0, i))
            cands.append((i, len(s) - 1))

        for cand in cands:
            # longest common prefix of best and cand
            resSize = 0
            l = 0
            r = len(s) - 1
            while l <= r:
                m = (l + r) // 2
                h1 = hashPf(m, *best)
                h2 = hashPf(m, *cand)
                if h1 == h2:
                    resSize = m + 1
                    l = m + 1
                else:
                    r = m - 1
            
            if resSize == len(s):
                continue
            if charAt(resSize, *cand) < charAt(resSize, *best):
                best = cand

        return ''.join(charAt(i, *best) for i in range(len(s)))

        
